# Gandalphaba Gray Eye — Microsoft Foundry scaffold

This is a local Microsoft Foundry hosted-agent scaffold for Gandalphaba, the
operational schema and synthetic-memory implementer for VUORSE-VORTEX. It is
not deployed and has no configured Foundry project.

## Authority and operating boundary

- Follow the repository's `policies/`, then
  `manifests/corpus/source_manifest.json`, then the source files.
- Keep every material claim labeled and tied to a repository-relative source.
  Draft and unknown canon statuses are not settled canon.
- Search only returns `public` and `behavioral` hits. Behavioral sources may
  shape style, not be stated as world fact.
- Generated outputs remain provisional. Gandalphaba cannot promote or seal
  canon, resolve contradictions without a ruling, or expose sealed/private
  material.
- Routine writes are limited to Gandalphaba's dedicated
  `worldforge/gandalphaba/` and `manifests/runs/gandalphaba/` areas, the
  existing `worldforge/worldforge/lore-index-2.0/`, and the existing
  `embeddings/indexes/` output. This avoids treating every provisional
  WorldForge report as an approved working source.
- Existing working files can only be replaced after reading them and supplying
  the matching SHA-256. Pruning is available only when the user explicitly
  requests removal of one exact path; the agent inspects and hash-checks that
  regular file, archives it with a receipt, and can restore it by archive ID.
  Wildcards, directory/recursive deletion, quarantine access, commits, and
  pull requests are not available.

## Local setup

The agent requires a Foundry project endpoint and a model deployment to answer
messages. Neither is configured by this scaffold. Do not provision Azure
resources without an explicit request.

1. Copy `foundry.env.template` to `.env` in the service source folder.
2. Set `FOUNDRY_PROJECT_ENDPOINT` and `AZURE_AI_MODEL_DEPLOYMENT_NAME` for an
   existing project, then keep `VUORSE_REPO_ROOT` pointed at this repository
   root.
3. From this project directory, use `azd ai agent run --no-client` and invoke
   it locally with `azd ai agent invoke --local "<request>"`.

The local workspace bridge intentionally fails when the repository is not
mounted. Before cloud deployment, replace it with an authenticated VUORSE API
or storage/toolbox connection that enforces the same disclosure and write
allowlists. Do not expose the local filesystem or deploy the repository corpus
inside the agent container.

## Tools

- `search_vuorse`: searches the existing Cortex index and filters results to
  public/behavioral visibility. It errors if the index is missing or unbuilt.
- `read_working_file_tool`: reads text artifacts only within approved working
  areas and returns their SHA-256.
- `write_working_file_tool`: creates or hash-checked replaces text artifacts
  within approved working areas.
- `inspect_prune_target_tool` and `prune_exact_file_tool`: only for an explicit
  request to remove one exact file; the original is archived with a receipt.
- `restore_pruned_file_tool`: restores one archived file by its archive ID.
- `rebuild_vuorse_corpus_index`: rebuilds the existing routed index when the
  user explicitly asks. Sealed material may be processed internally by the
  existing firewall-aware indexer, but search never returns sealed or
  non-public/non-behavioral hits.
