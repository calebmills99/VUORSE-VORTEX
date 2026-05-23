#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "vastai>=0.2",
#   "typer>=0.12",
#   "rich>=13.7",
#   "python-dotenv>=1.0",
# ]
# ///
"""Provision a VUORSE-VORTEX-tuned Vast.ai GPU box (on-demand hourly).

This is the sanctioned cloud-agent provisioner for VUORSE-VORTEX. It enforces the
project's GPU-first runtime contract by pre-baking ``CORTEX_REQUIRE_GPU=1`` and
``CORTEX_DEVICE=cuda`` into the launched container, and by refusing shapes that
fall under the published hardware floor (500 GB disk, 32 GB VRAM, 99% reliability,
North America).

The reconciled template (``vuorse-vortex-full``) exposes three access surfaces:

* **SSH** on port 22 (direct, not proxied)
* **JupyterLab** on port 8080 (auto-started by ``vastai/pytorch`` when
  ``runtype=jupyter_direct_ssh``; ``jupyter_dir=/workspace``)
* **XFCE desktop** via noVNC on port 6080 / raw VNC on port 5901, brought up by
  the on-start command using TigerVNC + websockify

The script is **non-destructive by default**. Without ``--launch`` it performs
template reconciliation and offer search only, then prints what it *would* have
spun up. Launching boots an **on-demand hourly** instance — billing accrues at
the offer's ``dph_total`` rate until the instance is destroyed. No prepay or
reserved contract is created.

Run::

    uv run scripts/vast_provision.py                          # dry-run
    uv run scripts/vast_provision.py --launch                 # real launch (hourly)
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# --------------------------------------------------------------------------- #
# Constants — the "optimal for this repo" defaults                            #
# --------------------------------------------------------------------------- #

TEMPLATE_NAME = "vuorse-vortex-full"
IMAGE = "vastai/pytorch"
# CUDA floor is 13.1+ per project policy. Vast.ai's ``cuda-*-auto`` images cap at
# ``cuda-13.0.2-auto`` (April 2026 fleet), which is below the floor. The only
# Vast images that ship CUDA 13.1+ runtime are the ``mini`` variants tagged
# ``cuda-13.2``. ``mini`` strips the auto-Jupyter convenience layer, so the
# onstart command below installs jupyterlab + uvicorn explicitly. The image's
# preinstalled torch is irrelevant — scripts/vast_startup.sh tears it down and
# rebuilds a project venv against cu132 wheels anyway.
IMAGE_TAG = "2.11.0-cu130-cuda-13.2-mini-py312-2026-04-15"

MIN_DISK_GB = 500
MIN_GPU_RAM_GB = 32
MIN_RELIABILITY = 0.99
# Compute capability floor, expressed as Vast.ai's integer-encoded value
# (capability * 100). 800 = Ampere (A100, A40, A4000-A6000, RTX 30-series).
# Below 800 means Volta (V100 = 700) or older, which lack bf16, FlashAttention,
# and the kernel ISA modern torch/transformers builds expect. We got a V100 on
# a previous run and it could not run our torch+CUDA stack; this floor stops
# Vast from handing us one again.
#  • 700 = Volta (V100)        ← rejected
#  • 750 = Turing (T4, RTX 20)
#  • 800 = Ampere (A100, A40, A6000, RTX 30)  ← floor
#  • 860 = Ampere consumer    (RTX 3090)
#  • 890 = Ada Lovelace       (RTX 4090, L40)
#  • 900 = Hopper             (H100)
MIN_COMPUTE_CAP = 800
NA_GEOS = ["US", "CA", "MX"]
DEFAULT_NUM_GPUS = 1
DEFAULT_MAX_DPH = 5.00  # safety cap: refuse to launch above $5/hr without override

# Public repo cloned onto the box on first boot. No auth needed.
# Hyphen, not underscore — must match the real GitHub remote and the URL
# referenced by scripts/vast_startup.sh + README.md. A typo here used to send
# the onstart command at an `_` URL that 404s, after which `|| true` silently
# moved on; the new bootstrap aborts loudly if the clone fails.
GH_REPO_URL = "https://github.com/calebmills99/VUORSE-VORTEX.git"

# Default noVNC/VNC password. Override per-instance via the Vast.ai env editor;
# the onstart reads ${VNC_PASSWORD:-vuorse} so this is just a fallback.
DEFAULT_VNC_PASSWORD = "vuorse"

# Default JupyterLab token. The ``mini`` image we now use does NOT auto-start
# Jupyter (unlike the old ``-auto`` image), so the onstart launches it itself
# with this token. Override per-instance via the Vast.ai env editor.
DEFAULT_JUPYTER_TOKEN = "vuorse-vortex"

# Port surface for the full template:
#   22   — SSH (direct)
#   8000 — FastAPI (vuorse_vortex.api:app)
#   8080 — Jupyter Lab (we launch it in onstart since the mini image lacks auto-Jupyter)
#   6080 — noVNC web client → XFCE desktop on display :1
#   5901 — raw VNC (TigerVNC) on display :1, for native VNC clients
ENV_FLAGS = (
    "-e CORTEX_REQUIRE_GPU=1 "
    "-e CORTEX_DEVICE=cuda "
    "-e CUDA_VISIBLE_DEVICES=0 "
    "-e HF_HOME=/workspace/.cache/huggingface "
    f"-e VNC_PASSWORD={DEFAULT_VNC_PASSWORD} "
    f"-e JUPYTER_TOKEN={DEFAULT_JUPYTER_TOKEN} "
    "-p 22:22 "
    "-p 8000:8000 "
    "-p 8080:8080 "
    "-p 6080:6080 "
    "-p 5901:5901"
)

# Desktop bootstrap: XFCE + TigerVNC + noVNC. Runs once on first container boot.
# Idempotent on re-runs — the package installs become no-ops and vncserver/websockify
# guards swallow "already running" errors so a restart doesn't double-launch them.
DESKTOP_SETUP = (
    "export DEBIAN_FRONTEND=noninteractive; "
    "apt-get update; "
    "apt-get install -y --no-install-recommends "
    "xfce4 xfce4-terminal dbus-x11 x11-xserver-utils xauth "
    "tigervnc-standalone-server tigervnc-common "
    "novnc websockify; "
    "mkdir -p /root/.vnc; "
    'printf "%s\\n" "${VNC_PASSWORD:-vuorse}" | vncpasswd -f > /root/.vnc/passwd; '
    "chmod 600 /root/.vnc/passwd; "
    'printf "#!/bin/sh\\nunset SESSION_MANAGER\\nunset DBUS_SESSION_BUS_ADDRESS\\n'
    'exec startxfce4\\n" > /root/.vnc/xstartup; '
    "chmod +x /root/.vnc/xstartup; "
    "pgrep -f 'Xtigervnc :1' >/dev/null 2>&1 || "
    "vncserver :1 -geometry 1920x1080 -depth 24 -localhost no -SecurityTypes VncAuth; "
    "pgrep -f 'websockify.*6080' >/dev/null 2>&1 || "
    "websockify -D --web=/usr/share/novnc 6080 localhost:5901"
)

# Pre-warm the runtime extras declared in pyproject.toml and clone the (public)
# repo so the box is ready for `uv sync --extra gpu` without a cold install.
# Then bring up the XFCE desktop behind noVNC.
#
# Clone behavior: the script exits the container's onstart with a non-zero
# status if `git clone` fails AND the target directory is also absent, instead
# of silently moving on. Previously a typoed URL would 404, the `|| true`
# swallowed the failure, and the user's first SSH would land on a box without
# the repo — easy to miss because the desktop and Jupyter would still work.
# The explicit `test -d ... || exit 1` makes the template bootstrap fail loudly
# so misconfiguration shows up in the Vast.ai instance logs, not later.
# JupyterLab boot. The mini-py312-cuda-13.2 image we now use does not auto-start
# Jupyter (only the old ``-auto`` family did), so we install + launch it from the
# onstart. We bind to 0.0.0.0 because Vast.ai's port-map proxies external traffic
# through the container interface; the JUPYTER_TOKEN env (see ENV_FLAGS) gates
# access. ``setsid`` detaches the process so onstart can complete; output goes
# to /var/log/jupyterlab.log for debug.
JUPYTER_LAUNCH = (
    "mkdir -p /workspace/notebooks; "
    "setsid nohup jupyter lab "
    "--no-browser --ip=0.0.0.0 --port=8080 "
    "--ServerApp.root_dir=/workspace --ServerApp.allow_root=True "
    '--ServerApp.token="${JUPYTER_TOKEN:-vuorse-vortex}" '
    "--ServerApp.password='' "
    ">/var/log/jupyterlab.log 2>&1 < /dev/null &"
)

ONSTART_CMD = (
    "set -e; "
    "env >> /etc/environment; "
    "curl -LsSf https://astral.sh/uv/install.sh | sh; "
    'export PATH="$HOME/.local/bin:$PATH"; '
    # cu132 wheels (CUDA 13.2 — satisfies the project's 13.1+ floor). The image
    # itself ships cuda-13.2 runtime libs; the wheel ships its own bundled libs
    # too so even if Vast.ai swaps the base image's CUDA toolchain, torch still
    # finds compatible runtime. Older wheel channels (cu130 and below) violate
    # the floor and must not be reintroduced here.
    "uv pip install --system --index-url https://download.pytorch.org/whl/cu132 "
    "'torch>=2.12'; "
    "uv pip install --system "
    "'sentence-transformers>=3.0' 'chromadb>=0.5' 'faiss-cpu>=1.8' "
    "'pydantic>=2.7' 'typer>=0.12' 'rich>=13.7' 'jsonschema>=4.22' 'orjson>=3.10' "
    "'python-dotenv>=1.0' 'numpy>=1.26' 'tqdm>=4.66' "
    "'fastapi>=0.136.1' 'uvicorn>=0.47.0' 'jinja2>=3.1.6' "
    "'jupyterlab>=4.2'; "
    "mkdir -p /workspace && cd /workspace && "
    f"(test -d VUORSE-VORTEX/.git || git clone {GH_REPO_URL}); "
    "test -d /workspace/VUORSE-VORTEX/.git || "
    "{ echo FATAL: VUORSE-VORTEX clone did not produce a git repo at "
    "/workspace/VUORSE-VORTEX; exit 1; }; "
    f"{JUPYTER_LAUNCH} "
    f"{DESKTOP_SETUP}"
)

# --------------------------------------------------------------------------- #
# Rich consoles — magenta headings to match src/vuorse_vortex/gpu.py          #
# --------------------------------------------------------------------------- #

console = Console()
err_console = Console(stderr=True)

app = typer.Typer(
    add_completion=False,
    help="VUORSE-VORTEX Vast.ai provisioner. Dry-run by default; pass --launch to spend.",
)


# --------------------------------------------------------------------------- #
# Options bundle                                                              #
# --------------------------------------------------------------------------- #


@dataclass
class ProvisionOptions:
    min_disk: int
    min_vram: int
    min_reliability: float
    min_compute_cap: int
    countries: list[str]
    image: str
    tag: str
    num_gpus: int
    max_dph: float
    launch: bool
    template_only: bool
    allow_downgrade: bool


    @property
    def countries_joined(self) -> str:
        return ",".join(self.countries)


# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #


def load_api_key() -> str:
    """Read VAST_API_KEY from a repo-root .env, falling back to the process env."""
    repo_root = Path(__file__).resolve().parent.parent
    load_dotenv(repo_root / ".env")
    key = os.getenv("VAST_API_KEY", "").strip()
    if not key:
        err_console.print(
            "[bold red]VAST_API_KEY is not set.[/bold red] "
            f"Add it to {repo_root / '.env'} (see {repo_root / '.env.example'}) "
            "or export it in the shell before re-running."
        )
        raise typer.Exit(code=2)
    return key


def make_client(api_key: str) -> Any:
    """Instantiate the vastai SDK client. Imported lazily so dry-help works offline."""
    try:
        from vastai import VastAI  # type: ignore[import-not-found]
    except ImportError as exc:  # pragma: no cover - declared in PEP 723 block
        err_console.print(
            "[bold red]vastai SDK not installed.[/bold red] "
            "This script is meant to be run via `uv run scripts/vast_provision.py` "
            "so the PEP 723 dependency block resolves automatically."
        )
        raise typer.Exit(code=2) from exc
    # raw=True requests machine-readable responses. In the inspected SDK build
    # the per-method paths already return parsed dicts/lists, but honoring the
    # flag both signals intent and is forward-compatible with future shapes —
    # _normalize_response() below absorbs the difference either way.
    return VastAI(api_key=api_key, raw=True)


def ensure_template(client: Any, opts: ProvisionOptions) -> str:
    """Idempotently materialize the VUORSE PyTorch template, returning its hash_id."""
    safe_image = opts.image.replace("/", "-").replace(":", "-")
    tpl_name = f"{TEMPLATE_NAME}-{safe_image}-{opts.tag}"
    console.print(f"[bold magenta]→ Reconciling template[/bold magenta] '{tpl_name}'…")
    raw = _safe_call(client, "search_templates")
    existing = _coerce_template_list(_normalize_response(raw))

    for tpl in existing:
        if tpl.get("name") == tpl_name:
            hash_id = str(tpl.get("hash_id") or tpl.get("id") or "")
            if hash_id:
                console.print(f"  [green]✓[/green] Found existing template hash={hash_id}")
                return hash_id

    console.print("  [yellow]·[/yellow] Not found — creating it now…")
    # The SDK's create_template translates ssh=True + jupyter=True + direct=True
    # into runtype=jupyter_direct_ssh internally and derives the ssh_direct/jupyter_direct
    # flags from those booleans; passing runtype/ssh_direct/tag directly is silently
    # dropped. image_tag is the supported kwarg for the image tag. jupyter_lab=True
    # makes the auto-started Jupyter come up as JupyterLab instead of classic Notebook.
    # If a future SDK release stops exposing these kwargs, fall back to a REST
    # POST /api/v0/template/ with the same payload.
    created = _normalize_response(
        _safe_call(
            client,
            "create_template",
            name=tpl_name,
            image=opts.image,
            image_tag=opts.tag,
            env=ENV_FLAGS,
            onstart_cmd=ONSTART_CMD,
            ssh=True,
            jupyter=True,
            jupyter_lab=True,
            jupyter_dir="/workspace",
            direct=True,
            disk_space=float(opts.min_disk),
            desc=(
                f"VUORSE-VORTEX PyTorch CUDA box: SSH + JupyterLab + noVNC. "
                f"Image: {opts.image}:{opts.tag}. CORTEX_REQUIRE_GPU=1 baked in."
            ),
        )
    )

    if isinstance(created, dict) and isinstance(created.get("template"), dict):
        created = created["template"]
    if not isinstance(created, dict):
        err_console.print(
            f"[bold red]create_template returned an unexpected payload:[/bold red] {created!r}"
        )
        raise typer.Exit(code=1)
    hash_id = str(created.get("hash_id") or created.get("id") or "")
    if not hash_id:
        err_console.print(
            f"[bold red]create_template succeeded but returned no hash_id:[/bold red] {created!r}"
        )
        raise typer.Exit(code=1)
    console.print(f"  [green]✓[/green] Created template hash={hash_id}")
    return hash_id


def build_query(opts: ProvisionOptions) -> tuple[str, str]:
    """Assemble the Vast.ai filter string + sort order (cheapest dph_total first)."""
    parts = [
        "rentable=true",
        "verified=true",
        f"reliability > {opts.min_reliability}",
        f"gpu_ram >= {opts.min_vram}",
        f"disk_space >= {opts.min_disk}",
        f"num_gpus >= {opts.num_gpus}",
        f"geolocation in [{opts.countries_joined}]",
        "cuda_max_good >= 12.0",
        f"compute_cap >= {opts.min_compute_cap}",
    ]
    return " ".join(parts), "dph_total"


def find_cheapest_offer(client: Any, query: str, order: str) -> dict[str, Any]:
    """Search offers and return the cheapest match, rendering the top-5 for transparency."""
    console.print(f"[bold magenta]→ Searching offers[/bold magenta] (order={order} asc)")
    console.print(f"  [dim]query:[/dim] {query}")
    raw = _safe_call(client, "search_offers", query=query, order=order, limit=20)
    offers = _coerce_offers(_normalize_response(raw))

    if not offers:
        err_console.print(
            "[bold red]No offers matched.[/bold red] Try loosening --min-vram, "
            "--min-disk, --min-reliability, or --countries."
        )
        raise typer.Exit(code=1)

    _render_offers_table(offers[:5])
    return offers[0]


def create_instance(
    client: Any,
    offer: dict[str, Any],
    template_hash: str,
    opts: ProvisionOptions,
) -> dict[str, Any]:
    """Launch the chosen offer using the VUORSE template."""
    offer_id = offer.get("id")
    if offer_id is None:
        err_console.print(f"[bold red]Chosen offer has no id:[/bold red] {offer!r}")
        raise typer.Exit(code=1)

    console.print(
        f"[bold magenta]→ Creating instance[/bold magenta] from offer {offer_id} "
        f"(@${offer.get('dph_total', '?')}/hr)…"
    )
    # Note: instances.create_instance() does NOT accept ssh=/jupyter= kwargs —
    # the `runtype` string is how protocols are selected. Passing ssh=True or
    # jupyter=True raises TypeError. "jupyter_direct_ssh" matches the template's
    # ssh+jupyter+direct combination and lets us hit Jupyter on 8080 and SSH on 22
    # without proxying through the Vast cloud.
    result = _normalize_response(
        _safe_call(
            client,
            "create_instance",
            id=offer_id,
            template_hash=template_hash,
            image=IMAGE,
            disk=opts.min_disk,
            runtype="jupyter_direct_ssh",
            label="vuorse-vortex",
        )
    )
    if not isinstance(result, dict):
        err_console.print(f"[bold red]create_instance returned:[/bold red] {result!r}")
        raise typer.Exit(code=1)

    if not result.get("success", True):
        err_console.print(f"[bold red]Vast.ai refused the launch:[/bold red] {result!r}")
        raise typer.Exit(code=1)

    console.print("  [green]✓[/green] Instance accepted by Vast.ai")
    return result


# --------------------------------------------------------------------------- #
# Internal utilities                                                          #
# --------------------------------------------------------------------------- #


def _safe_call(client: Any, method: str, **kwargs: Any) -> Any:
    """Invoke a vastai SDK method, surfacing a clean error if it's missing."""
    fn = getattr(client, method, None)
    if fn is None:
        err_console.print(
            f"[bold red]vastai SDK has no method '{method}'.[/bold red] "
            "The published SDK shape may have changed — pin a known-good version "
            "in the PEP 723 header (e.g. vastai==0.3.x)."
        )
        raise typer.Exit(code=2)
    try:
        return fn(**kwargs)
    except TypeError as exc:
        err_console.print(
            f"[bold red]vastai.{method} rejected its arguments:[/bold red] {exc}"
        )
        raise typer.Exit(code=2) from exc
    except Exception as exc:  # noqa: BLE001 — surface the underlying SDK error verbatim
        err_console.print(f"[bold red]vastai.{method} raised:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc


def _normalize_response(payload: Any) -> Any:
    """Coerce a vastai SDK response into native Python.

    Handles three shapes so future SDK changes don't break this script:

    * Already-decoded ``dict`` / ``list`` — returned untouched (current SDK).
    * JSON-encoded ``str`` / ``bytes`` — parsed via ``json.loads`` (forward
      compatibility with ``raw=True``).
    * Anything else — returned as-is so the caller can render a clean error.
    """
    if isinstance(payload, (bytes, bytearray)):
        payload = payload.decode("utf-8", errors="replace")
    if isinstance(payload, str):
        stripped = payload.strip()
        if stripped and stripped[0] in "[{":
            try:
                return json.loads(stripped)
            except json.JSONDecodeError:
                return payload
    return payload


def _coerce_template_list(raw: Any) -> list[dict[str, Any]]:
    """Normalize ``search_templates`` responses into a list of template dicts."""
    if raw is None:
        return []
    if isinstance(raw, list):
        return [t for t in raw if isinstance(t, dict)]
    if isinstance(raw, dict):
        value = raw.get("templates")
        if isinstance(value, list):
            return [t for t in value if isinstance(t, dict)]
    return []


def _coerce_offers(raw: Any) -> list[dict[str, Any]]:
    """Normalize the various shapes the SDK may return into a list of offer dicts."""
    if raw is None:
        return []
    if isinstance(raw, list):
        return [o for o in raw if isinstance(o, dict)]
    if isinstance(raw, dict):
        for key in ("offers", "results", "data"):
            value = raw.get(key)
            if isinstance(value, list):
                return [o for o in value if isinstance(o, dict)]
    return []


def _render_offers_table(offers: list[dict[str, Any]]) -> None:
    table = Table(
        title="Top candidates (cheapest first)",
        title_style="bold magenta",
        header_style="bold cyan",
    )
    for col in (
        "id",
        "gpu_name",
        "num_gpus",
        "gpu_ram",
        "disk_space",
        "reliability2",
        "geolocation",
        "dph_total",
    ):
        table.add_column(col)
    for o in offers:
        table.add_row(
            str(o.get("id", "?")),
            str(o.get("gpu_name", "?")),
            str(o.get("num_gpus", "?")),
            str(o.get("gpu_ram", "?")),
            str(o.get("disk_space", "?")),
            f"{o.get('reliability2', o.get('reliability', '?'))}",
            str(o.get("geolocation", "?")),
            f"${o.get('dph_total', '?')}",
        )
    console.print(table)


def _render_final_summary(
    instance: dict[str, Any],
    offer: dict[str, Any],
    opts: ProvisionOptions,
) -> None:
    instance_id = instance.get("new_contract") or instance.get("instance_id") or instance.get("id")
    ssh_host = instance.get("ssh_host") or offer.get("public_ipaddr") or "(provisioning…)"
    ssh_port = instance.get("ssh_port") or "(provisioning…)"
    public_ip = offer.get("public_ipaddr") or ssh_host
    hourly = float(offer.get("dph_total", 0.0) or 0.0)

    # noVNC/Jupyter/FastAPI ports are baked into ENV_FLAGS but Vast.ai remaps them
    # to high external ports per-instance; the dashboard is the canonical place to
    # discover the actual mappings. We still print the in-container ports so the
    # user knows what to look for in the "Open Ports" panel.
    table = Table(title="VUORSE box online (on-demand)", title_style="bold magenta")
    table.add_column("field", style="bold cyan")
    table.add_column("value")
    table.add_row("instance_id", str(instance_id))
    table.add_row("ssh", f"ssh root@{ssh_host} -p {ssh_port}")
    table.add_row("jupyter (in-container)", f"http://{public_ip}:8080/")
    table.add_row("fastapi (in-container)", f"http://{public_ip}:8000/")
    table.add_row("desktop / noVNC", f"http://{public_ip}:6080/vnc.html")
    table.add_row("raw VNC", f"{public_ip}:5901  (password: $VNC_PASSWORD)")
    table.add_row("dashboard", "https://cloud.vast.ai/instances/")
    table.add_row("billing", "on-demand hourly")
    table.add_row("hourly cost", f"${hourly:.4f}/hr")
    console.print(table)
    console.print(
        "[dim]Vast.ai remaps container ports to high external ports; check the "
        "instance's 'Open Ports' panel in the dashboard for the actual host:port "
        "mappings. The XFCE desktop bootstrap runs on first boot and takes ~2–3 "
        "minutes before noVNC at :6080 responds.[/dim]"
    )


# --------------------------------------------------------------------------- #
# CLI entry point                                                             #
# --------------------------------------------------------------------------- #


@app.command()
def provision(
    min_disk: int = typer.Option(
        MIN_DISK_GB, "--min-disk", help="Minimum disk in GB. VUORSE floor: 500."
    ),
    min_vram: int = typer.Option(
        MIN_GPU_RAM_GB, "--min-vram", help="Minimum GPU VRAM in GB. VUORSE floor: 32."
    ),
    min_reliability: float = typer.Option(
        MIN_RELIABILITY, "--min-reliability", help="Minimum reliability (0-1). VUORSE floor: 0.99."
    ),
    min_compute_cap: int = typer.Option(
        MIN_COMPUTE_CAP,
        "--min-compute-cap",
        help=(
            "Minimum CUDA compute capability * 100. VUORSE floor: 800 (Ampere). "
            "Excludes Volta (V100=700) and Turing (T4=750), which can't run our torch."
        ),
    ),
    countries: str = typer.Option(
        ",".join(NA_GEOS), "--countries", help="Comma-separated ISO country codes."
    ),
    image: str = typer.Option(
        IMAGE, "--image", help="Container image to run. Defaults to vastai/pytorch."
    ),
    tag: str = typer.Option(
        IMAGE_TAG, "--tag", help="Pinned image tag. Never use 'latest' (per Vast.ai docs)."
    ),
    num_gpus: int = typer.Option(DEFAULT_NUM_GPUS, "--num-gpus", help="GPUs per instance."),
    max_dph: float = typer.Option(
        DEFAULT_MAX_DPH, "--max-dph", help="Refuse to launch above this $/hr cap."
    ),
    launch: bool = typer.Option(
        False,
        "--launch/--dry-run",
        help="Without --launch this is a dry-run: no instance, no charges.",
    ),
    template_only: bool = typer.Option(
        False, "--template-only", help="Reconcile the template and exit. Skips search/launch."
    ),
    allow_downgrade: bool = typer.Option(
        False,
        "--allow-downgrade",
        help="Permit running below the VUORSE hardware floor (32 GB VRAM / 500 GB disk).",
    ),
    api_key: str = typer.Option(
        "", "--api-key", help="Override VAST_API_KEY from .env (not recommended)."
    ),
) -> None:
    """Reconcile template, search NA offers, and (optionally) launch on-demand hourly."""
    opts = ProvisionOptions(
        min_disk=min_disk,
        min_vram=min_vram,
        min_reliability=min_reliability,
        min_compute_cap=min_compute_cap,
        countries=[c.strip().upper() for c in countries.split(",") if c.strip()],
        image=image,
        tag=tag,
        num_gpus=num_gpus,
        max_dph=max_dph,
        launch=launch,
        template_only=template_only,
        allow_downgrade=allow_downgrade,
    )


    console.print(
        Panel.fit(
            "[bold magenta]VUORSE-VORTEX • Vast.ai provisioner[/bold magenta]\n"
            f"mode: {'LAUNCH' if opts.launch else 'DRY-RUN'}   "
            f"floor: ≥{opts.min_vram}GB VRAM / ≥{opts.min_disk}GB disk / "
            f"reliability >{opts.min_reliability}   "
            f"geo: {opts.countries_joined}",
            border_style="magenta",
        )
    )

    if not opts.allow_downgrade:
        if (
            opts.min_disk < MIN_DISK_GB
            or opts.min_vram < MIN_GPU_RAM_GB
            or opts.min_compute_cap < MIN_COMPUTE_CAP
        ):
            err_console.print(
                f"[bold red]Refusing to operate below the VUORSE GPU-runtime floor[/bold red] "
                f"(min-vram≥{MIN_GPU_RAM_GB}, min-disk≥{MIN_DISK_GB}, "
                f"min-compute-cap≥{MIN_COMPUTE_CAP}). "
                "Pass --allow-downgrade to override."
            )
            raise typer.Exit(code=2)

    resolved_key = api_key.strip() or load_api_key()
    client = make_client(resolved_key)

    template_hash = ensure_template(client, opts)

    if opts.template_only:
        console.print("[bold green]Template reconciled.[/bold green] Exiting (--template-only).")
        return

    query, order = build_query(opts)
    offer = find_cheapest_offer(client, query, order)

    hourly = float(offer.get("dph_total", 0.0) or 0.0)
    if hourly > opts.max_dph:
        err_console.print(
            f"[bold red]Cheapest matching offer ${hourly}/hr exceeds --max-dph ${opts.max_dph}."
            "[/bold red] Raise --max-dph or loosen filters."
        )
        raise typer.Exit(code=1)

    if not opts.launch:
        console.print(
            Panel.fit(
                "[bold yellow][DRY-RUN][/bold yellow] No instance created, no charges incurred.\n"
                f"Would launch offer [bold]{offer.get('id')}[/bold] "
                f"({offer.get('gpu_name')} ×{offer.get('num_gpus')}) "
                f"on-demand @ [bold]${hourly:.4f}/hr[/bold]. "
                "Billing accrues hourly until the instance is destroyed.\n"
                "Re-run with [bold cyan]--launch[/bold cyan] to spend.",
                border_style="yellow",
            )
        )
        return

    instance = create_instance(client, offer, template_hash, opts)
    instance_id = (
        instance.get("new_contract") or instance.get("instance_id") or instance.get("id")
    )
    if instance_id is None:
        err_console.print(
            f"[bold red]Launched, but no instance id was returned:[/bold red] {instance!r}"
        )
        raise typer.Exit(code=1)

    _render_final_summary(instance, offer, opts)


def main() -> None:
    try:
        app()
    except typer.Exit:
        raise
    except KeyboardInterrupt:
        err_console.print("\n[bold yellow]Interrupted.[/bold yellow] No further action taken.")
        sys.exit(130)


if __name__ == "__main__":
    main()
