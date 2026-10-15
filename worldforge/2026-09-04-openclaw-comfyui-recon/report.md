# VUORSE-VORTEX Gray Eye Reconnaissance: OpenClaw and ComfyUI Expert

*A realm is rarely undone by the dragon everyone can see. It is the unlabeled door behind the throne that causes the trouble.*

*Here, the doors are repositories, manifests, runtime boundaries, and one rather ambitious video agent.*

## Run frame

- **assumption** Change point: integrate ComfyUI Expert with OpenClaw as a reliable specialist system inside VUORSE-VORTEX. Provenance: Caleb's request in the 2026-09-04 Telegram session.
- **canon** Observation cutoff: 2026-09-04 16:48 PDT. Provenance: the requested run parameters.
- **assumption** Interval: the next integration phase, from current deployment through the first repeatable canon-aware production workflow. Provenance: inferred from the active OpenClaw and ComfyUI work.
- **assumption** Domains: lore and canon, repository architecture, indexing and canon firewall, agent orchestration, Windows and WSL, OpenClaw, ComfyUI, project state, and creative production. Provenance: requested run parameters.
- **canon** Temporal mode: `prospective`. Provenance: requested run parameters.

## Baseline

- **canon** `/mnt/c/runb2/vuorse-vortex` is the outer Git repository, with remote `https://github.com/calebmills99/VUORSE-VORTEX.git`, currently on branch `feat/indexer-agent-and-canon-firewall`. Provenance: `.git/config` and live Git inspection.
- **canon** The outer repository combines a lore corpus, generated indexes, agent definitions, Python tooling, tests, worldforge artifacts, and a nested ComfyUI production subsystem. Provenance: `canon/`, `manifests/`, `agents/`, `vuorse_vortex/`, `tests/`, `worldforge/`, and `comfyui-expert/`.
- **canon** The corpus manifest names itself `VUORSE-VORTEX Source Corpus`, records 48 sources, identifies 16 sealed sources, and says the finale is not included. Provenance: `manifests/corpus/source_manifest.json`.
- **canon** The canon tree is divided into 18 top-level domains, including books one and two, characters, cosmology, artifacts, organizations, places, relationships, rituals, story arcs, open threads, projects, and the television series bible. Provenance: `canon/`.
- **canon** Two differently named Book Two directories coexist: `canon/2-words-of_weaver_book_two/` and `canon/2_words_of_weaver_book_two/`. Provenance: `canon/` directory inventory.
- **canon** The generated corpus indexes currently contain 19 list entries in the entity index and 71 list entries in the relationship index. Provenance: `manifests/corpus/entity_index.json` and `manifests/corpus/relationship_index.json`.
- **canon** The Python package is named `vuorse-vortex`, version `0.1.0`, and contains modules for API, CLI, canon firewall behavior, graph operations, indexing, schema handling, synthesis, vectors, and walled execution. Provenance: `pyproject.toml` and `vuorse_vortex/`.
- **canon** The repository contains 59 files under `tests/`, including 19 `test_*.py` files. Provenance: `tests/` inventory.
- **canon** The outer repository's `README.md` and `AGENT.md` currently identify the project as `VideoAgent`, while the root `AGENTS.md` identifies itself as a Codex compatibility adapter. Provenance: `README.md`, `AGENT.md`, and `AGENTS.md`.
- **canon** `comfyui-expert/` is the only nested Git repository discovered beneath the outer repository. Provenance: nested `.git` inventory.
- **canon** The nested subsystem defines its own VideoAgent canon, skills, inventory, project state, and OpenClaw adapter. Provenance: `comfyui-expert/AGENT.md`, `comfyui-expert/skills/`, `comfyui-expert/state/`, and `comfyui-expert/openclaw/`.
- **canon** The live integration now has a WSL-native `video-agent` workspace, the official Comfy provider, and a reachable Windows ComfyUI 0.28.0 endpoint at `http://172.27.208.1:8188`. Provenance: live OpenClaw configuration, `~/.openclaw/workspaces/video-agent/`, and ComfyUI `/system_stats`.
- **canon** The connector source is `comfyui-expert/openclaw/connect-openclaw-comfyui.sh`; the Windows launcher is `D:\ComfyUI312\run_comfyui.bat` and now binds ComfyUI with `--listen 0.0.0.0`. Provenance: those two files and the successful WSL health probe.
- **canon** The outer working tree already contains hundreds of tracked modifications, so current filesystem state cannot be treated as equivalent to the last commit. Provenance: live `git status --porcelain` count at the observation cutoff.

## What the realm actually is

- **inference** VUORSE-VORTEX is not merely a story archive. It is becoming a canon-governed production platform in which narrative sources feed indexes and relationship graphs, agents interpret those artifacts, and production tools turn interpretations into media. Confidence: high. Provenance: `canon/`, `manifests/corpus/`, `vuorse_vortex/indexing.py`, `vuorse_vortex/graphd.py`, `vuorse_vortex/firewall.py`, `agents/`, and `comfyui-expert/`.
- **inference** The canon firewall and sealed-source concepts are intended to stop generated or provisional material from silently becoming authority. Confidence: high. Provenance: branch name `feat/indexer-agent-and-canon-firewall`, `vuorse_vortex/firewall.py`, `vuorse_vortex/walled.py`, `manifests/corpus/source_manifest.json`, and associated tests.
- **inference** ComfyUI Expert is a production specialist, not the sovereign project agent. Its own doctrine is inventory-first and workflow-focused, which is narrower than whole-world canon stewardship. Confidence: high. Provenance: `comfyui-expert/AGENT.md` and `comfyui-expert/docs/architecture.md`.
- **inference** The outer root's present VideoAgent bootstrap files blur that hierarchy by making the subsystem appear to govern the entire project. Confidence: high. Provenance: root `README.md`, root `AGENT.md`, root `AGENTS.md`, and nested `comfyui-expert/AGENT.md`.

## Nodes

- **canon** Canon corpus: authoritative and sealed narrative sources under `canon/`, catalogued by `manifests/corpus/source_manifest.json`.
- **canon** Canon indexes: machine-readable entity and relationship projections under `manifests/corpus/`.
- **canon** Canon firewall runtime: Python modules under `vuorse_vortex/`, especially `firewall.py`, `walled.py`, `indexing.py`, `graphd.py`, and `schemas.py`.
- **canon** Agent council: domain personas and specialists under `agents/`.
- **canon** Production specialist: the nested `comfyui-expert/` repository and its 15 OpenClaw-discoverable skills.
- **canon** OpenClaw runtime: WSL-native Gateway, plugin store, `video-agent`, sessions, and deployed workspace under `~/.openclaw/`.
- **canon** ComfyUI runtime: Windows-hosted ComfyUI, models, nodes, GPU, and output storage under `D:\ComfyUI312\`.
- **canon** Forge artifacts: exploratory and production-facing reports under `worldforge/`.
- **assumption** Project steward: Caleb is the final authority for canon promotion and architectural choices. Provenance: user role in the current conversation.

## Admitted causal edges

- **inference** `canon sources -> corpus manifests and indexes`: indexing converts narrative sources into machine-readable retrieval structures. Sign: positive. Lag: build-time. Context: index generation. Confidence: high. Provenance: `vuorse_vortex/indexing.py`, `vuorse_vortex/cli.py`, and `manifests/corpus/`.
- **inference** `sealed-source policy -> canon firewall -> agent context`: the firewall constrains what generated systems may treat as settled. Sign: positive when enforced, negative when bypassed. Lag: immediate per request. Confidence: high. Provenance: `vuorse_vortex/firewall.py`, `vuorse_vortex/walled.py`, and `manifests/corpus/source_manifest.json`.
- **inference** `agent interpretation -> ComfyUI workflow selection`: narrative and character requirements become model, node, prompt, and workflow choices. Sign: mixed. Lag: one production turn. Confidence: high. Provenance: `comfyui-expert/AGENT.md` and `comfyui-expert/skills/`.
- **canon** `OpenClaw WSL -> HTTP -> Windows ComfyUI`: the deployed provider submits workflows over the ComfyUI API and retrieves outputs. Sign: positive. Lag: immediate plus generation time. Confidence: high. Provenance: live provider configuration and `comfyui-expert/openclaw/connect-openclaw-comfyui.sh`.
- **inference** `Windows source -> deployment copy -> WSL agent`: deployment creates a runtime snapshot. Sign: positive for filesystem reliability, mixed for freshness. Lag: until the next deployment. Confidence: high. Provenance: `comfyui-expert/openclaw/connect-openclaw-comfyui.sh`.
- **inference** `root bootstrap ambiguity -> wrong governing doctrine`: when the outer project loads a VideoAgent root specification, project-wide work can be routed through production doctrine before canon governance is established. Sign: negative. Lag: first substantive turn. Confidence: high. Provenance: root `AGENT.md` and `README.md`.
- **inference** `dirty working tree -> uncertain baseline -> unreliable promotion`: hundreds of tracked modifications make commit history an incomplete description of current canon and software state. Sign: negative. Lag: immediate during comparison, rollback, or review. Confidence: high. Provenance: live Git status.

## Propagation from the change point

### Primary chain

1. **simulation** OpenClaw receives a creative or production request through the main assistant.
2. **simulation** Gandalf performs project-wide reconnaissance and identifies the applicable canon sources, sealed boundaries, and subsystem owner.
3. **simulation** A project-level orchestrator produces a canon-bounded brief rather than handing raw user intent directly to VideoAgent.
4. **simulation** `video-agent` validates local inventory and converts the brief into an executable ComfyUI workflow.
5. **simulation** The official Comfy provider submits the workflow from WSL to Windows ComfyUI and returns generated media.
6. **simulation** Output metadata and production notes return to a non-canon project or worldforge area.
7. **simulation** Caleb explicitly promotes only selected narrative consequences into canon.

- **inference** This chain preserves specialist autonomy while preventing the production subsystem from becoming an accidental source of lore authority. Confidence: high. Provenance: the existing canon firewall architecture plus the nested VideoAgent doctrine.

## Branches

### Branch A: Governed specialist pipeline

- **simulation** Weight: `likely`, if root governance is repaired.
- **simulation** Gandalf or the project orchestrator establishes canon and assumptions, VideoAgent handles production, and promotion remains explicit.
- **inference** Result: higher production speed without sacrificing provenance. Confidence: high. Provenance: existing manifests, firewall modules, VideoAgent inventory discipline, and current OpenClaw integration.

### Branch B: Snapshot drift

- **simulation** Weight: `plausible`.
- **simulation** Windows sources change after deployment, while the WSL-native `video-agent` continues using an older copied skill, inventory, or project file.
- **inference** Result: technically valid generations based on stale project context. Confidence: high. Provenance: one-way deployment behavior in `comfyui-expert/openclaw/connect-openclaw-comfyui.sh`.

### Branch C: Canon duplication becomes semantic duplication

- **simulation** Weight: `plausible`.
- **simulation** Both Book Two directory variants are indexed or maintained independently, causing duplicate entities, conflicting passages, or unstable provenance paths.
- **inference** Result: relationship counts and retrieval confidence become misleading even when every individual parser succeeds. Confidence: medium. Provenance: the two Book Two directories under `canon/`.

### Branch D: Production doctrine captures the throne

- **simulation** Weight: `stretch`, but already foreshadowed by current root files.
- **simulation** Root-level VideoAgent instructions remain the first authority seen by tools, so project work is optimized for executability and inventory rather than canon governance.
- **inference** Result: polished media can outrun the system that decides what is true. Confidence: medium. Provenance: root `AGENT.md`, root `README.md`, and the nested `comfyui-expert/` doctrine.

### Counterfactual control

- **counterfactual** If VUORSE-VORTEX had no canon firewall, no sealed-source manifest, and no outer project tooling, then making VideoAgent the root authority would be coherent. That is not the current timeline: those governing systems already exist under `vuorse_vortex/`, `manifests/corpus/`, and `canon/`.

## Contradictions and drift

- **canon** Root identity conflict: the outer repository is named `vuorse-vortex` in `pyproject.toml` and Git, but root `README.md` and `AGENT.md` describe VideoAgent. Provenance: `pyproject.toml`, `.git/config`, `README.md`, and `AGENT.md`.
- **canon** Canon path duplication: two Book Two roots differ by hyphen versus underscore. Provenance: `canon/2-words-of_weaver_book_two/` and `canon/2_words_of_weaver_book_two/`.
- **canon** Runtime path split: source lives on Windows-mounted storage while the active OpenClaw workspace lives in WSL-native storage. Provenance: repository path and live `video-agent` workspace configuration.
- **inference** Authority gap: no installed Gandalf skill or project-level OpenClaw agent currently governs the whole outer repository. Confidence: high. Provenance: searches under `skills/`, `agents/`, and the live OpenClaw agent roster at the cutoff.
- **canon** Test execution initially failed because the declared `dev` extra had not been installed. After `uv sync --extra dev`, the suite completed with 213 passed and 2 skipped tests. Provenance: `pyproject.toml` and live command results on 2026-09-04.

## Recommended order of operations

1. **simulation** Restore project-level identity and authority at the outer root. The root bootstrap should describe VUORSE-VORTEX and route production work to `comfyui-expert/`, not present VideoAgent as the whole realm.
2. **simulation** Install Gandalf as an actual project-visible skill with its supporting label, human-node, report, and artifact references.
3. **simulation** Declare an authority manifest: sealed canon sources, generated indexes, provisional worldforge outputs, production assets, and explicit promotion rules.
4. **simulation** Resolve the two Book Two roots by identifying the authoritative path and recording the other as alias, migration source, or duplicate.
5. **simulation** Add a project-level OpenClaw agent for VUORSE-VORTEX. Keep `video-agent` as a callable specialist rather than binding it as sovereign over the whole project.
6. **simulation** Add a deployment receipt containing source commit, dirty-tree fingerprint, inventory timestamp, workflow hash, and endpoint used. Reject silent WSL snapshot drift.
7. **simulation** Make ComfyUI endpoint refresh an explicit startup check because the WSL host address may change between sessions.
8. **simulation** Restore the test environment so the existing test suite can execute, then add integration checks for canon gating, specialist delegation, provider health, and artifact provenance.
9. **simulation** Run one canon-bounded production request end to end and confirm that generated output lands outside canon until promoted.

## Canon-promotion candidates

These are not canon unless Caleb promotes them.

- **simulation** Candidate: VUORSE-VORTEX root governance outranks every subsystem adapter.
- **simulation** Candidate: Gandalf reconnaissance is mandatory before implementation affecting more than one VUORSE-VORTEX domain.
- **simulation** Candidate: VideoAgent may select production methods but may not promote lore.
- **simulation** Candidate: generated media, prompts, and production notes remain provisional until explicitly promoted.
- **simulation** Candidate: Windows owns source and ComfyUI runtime; WSL owns OpenClaw runtime; deployment receipts join the two.
- **simulation** Candidate: corpus indexes are projections of canon, not independent canon sources.

## Verification

- **canon** Required run frame present: change point, observation cutoff, interval, domains, and exactly one temporal mode.
- **canon** Label discipline present: `canon`, `inference`, `assumption`, `simulation`, and `counterfactual` are distinguished; no counterfactual branch was required for this prospective run.
- **canon** Provenance present on every baseline and inference claim through repository paths, live runtime evidence, or named assumptions.
- **canon** Source exclusions honored: `.agent-quarantine` was not enumerated or read.
- **canon** Project source was not edited by the reconnaissance; this report is the only intended artifact.
- **canon** Runtime verification completed after installing the existing `dev` extra: 213 tests passed, 2 were skipped, and pytest emitted one cache-permission warning for `.pytest_cache`.

**Gandalf the Gray Eye**
