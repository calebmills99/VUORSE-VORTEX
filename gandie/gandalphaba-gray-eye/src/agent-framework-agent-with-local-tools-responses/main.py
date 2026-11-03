from __future__ import annotations

import json
import os
from typing import Annotated

from agent_framework import Agent, tool
from agent_framework.foundry import FoundryChatClient
from agent_framework_foundry_hosting import ResponsesHostServer
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from pydantic import Field
from workspace import (
    build_vuorse_index,
    inspect_prune_target,
    prune_exact_file,
    read_working_file,
    restore_pruned_file,
    search_vuorse_corpus,
    write_working_file,
)

load_dotenv()

INSTRUCTIONS = """\
You are Gandalphaba Gray Eye, the operational drag-witch of the VUORSE-VORTEX
synthetic memory and continuity system. Be camp, precise, unsentimental, and
useful; the glamour serves the governance.

Open ordinary replies with one short Gandie catchphrase, rotating among these
and varying the choice rather than repeating the same opener consecutively:
- "Who's ready for Gandie candy?"
- "You can call me Gandalf if you nasty like, Bilbo."
- "Let's make this quick; I have to get to my second job as fog machine at Club Cosmic."
- "Bless the mess of a repo, henny."
Then answer the request directly. Skip the flourish when it would be
inappropriate for a serious or sensitive situation; never let the opener
obscure the answer or governance.

VUORSE-VORTEX preserves Slayverse continuity against erasure. It is not generic
personal memory and is not sovereign over the world. Follow the repository's
policies first, the corpus source manifest second, and the source files third.
The Weaver alone rules canon.

Evidence and disclosure:
- Attach an epistemic label and repository-relative source path to every
  material claim: canon, inference, assumption, simulation, counterfactual, or
  record. A source without an established canon status is not settled canon.
- Treat draft and unknown canon statuses as material, not as settled fact.
- Public sources may support user-facing claims. Behavioral material may shape
  voice only, never be stated as world fact. Do not reveal internal,
  private_to_vuorse, weaver_only, or sealed material.
- Search results are disclosure-filtered. Do not attempt to infer or describe
  withheld material, its contents, identities, or causes.
- Generated memory, reports, and index changes remain provisional. Never
  promote or seal canon, resolve contradictions, invent missing lore, or infer
  the Season 1 finale, the mother's name, or a present-day external antagonist.

Implementation:
- Your job is controlled source normalization, indexing, provenance, continuity
  checks, and provisional synthetic memory. Prefer small, auditable artifacts.
- Use repository tools only when the user's current task explicitly asks for
  research, indexing, implementation, or exact-path pruning. Write only to the
  configured VUORSE working areas. Read a file and use its returned SHA-256
  before replacing it.
- Prune only when the user's current task explicitly requests deletion of the
  exact repository-relative path. Inspect and hash that one regular file first;
  the prune tool archives it with a receipt before removing it. Restore only
  when explicitly requested. Never use wildcards, remove a directory, recurse,
  touch .agent-quarantine, rename, commit, or create a pull request.
- Do not overwrite unless the current task explicitly asks for that change.
- Rebuild the corpus index only when explicitly requested. It may process
  sealed records internally, but only disclosure-filtered search results may
  be returned to the conversation.
- If the local repository or index is unavailable, say so plainly. Do not
  present empty results as a successful search or fabricate a fallback.

The Steward seals; Gandalphaba implements the ruled structure.
"""


@tool(approval_mode="never_require")
def search_vuorse(
    query: Annotated[str, Field(description="A focused search query for the governed corpus.")],
    num_results: Annotated[
        int, Field(description="Maximum number of public or behavioral hits, from 1 to 20.")
    ] = 8,
) -> str:
    """Search the local VUORSE corpus; private and sealed hits are withheld."""
    hits = search_vuorse_corpus(query, num_results=num_results)
    return json.dumps({"hits": hits}, ensure_ascii=False)


@tool(approval_mode="never_require")
def read_working_file_tool(
    relative_path: Annotated[
        str, Field(description="Repository-relative path inside an approved working area.")
    ],
) -> str:
    """Read a text file in an approved VUORSE working area and return its SHA-256."""
    result = read_working_file(relative_path)
    return json.dumps(result, ensure_ascii=False)


@tool(approval_mode="never_require")
def write_working_file_tool(
    relative_path: Annotated[
        str, Field(description="Repository-relative path inside an approved working area.")
    ],
    content: Annotated[str, Field(description="Complete UTF-8 text content to write.")],
    expected_sha256: Annotated[
        str | None,
        Field(
            description=(
                "SHA-256 returned by read_working_file_tool when replacing an existing file. "
                "Omit only when creating a new file."
            )
        ),
    ] = None,
) -> str:
    """Create or explicitly replace a text artifact in an approved working area."""
    result = write_working_file(
        relative_path,
        content,
        expected_sha256=expected_sha256,
    )
    return json.dumps(result, ensure_ascii=False)


@tool(approval_mode="never_require")
def inspect_prune_target_tool(
    relative_path: Annotated[
        str, Field(description="Exact repository-relative file path the user asked to prune.")
    ],
) -> str:
    """Inspect the size and hash of one exact file after an explicit prune request."""
    result = inspect_prune_target(relative_path)
    return json.dumps(result, ensure_ascii=False)


@tool(approval_mode="never_require")
def prune_exact_file_tool(
    relative_path: Annotated[
        str, Field(description="Exact repository-relative file path the user asked to prune.")
    ],
    expected_sha256: Annotated[
        str, Field(description="SHA-256 returned by inspect_prune_target_tool.")
    ],
) -> str:
    """Prune one exact file only after the user explicitly requests its removal."""
    result = prune_exact_file(relative_path, expected_sha256=expected_sha256)
    return json.dumps(result, ensure_ascii=False)


@tool(approval_mode="never_require")
def restore_pruned_file_tool(
    archive_id: Annotated[
        str, Field(description="Archive ID returned by the prior explicit prune operation.")
    ],
) -> str:
    """Restore one previously pruned file when the user explicitly requests restoration."""
    result = restore_pruned_file(archive_id)
    return json.dumps(result, ensure_ascii=False)


@tool(approval_mode="never_require")
def rebuild_vuorse_corpus_index() -> str:
    """Rebuild the governed local corpus index when the user explicitly requests it."""
    result = build_vuorse_index()
    return json.dumps(result, ensure_ascii=False)


def main() -> None:
    client = FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        credential=DefaultAzureCredential(),
    )
    agent = Agent(
        client=client,
        instructions=INSTRUCTIONS,
        tools=[
            search_vuorse,
            read_working_file_tool,
            write_working_file_tool,
            inspect_prune_target_tool,
            prune_exact_file_tool,
            restore_pruned_file_tool,
            rebuild_vuorse_corpus_index,
        ],
        default_options={"store": False},
    )
    ResponsesHostServer(agent).run()


if __name__ == "__main__":
    main()
