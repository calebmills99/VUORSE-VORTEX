# OpenClaw Adapter

The canonical VideoAgent behavior, routing, authority boundaries, inventory discipline, and operational doctrine live in `../AGENT.md` when this adapter is used in place, or `AGENT.md` in a flattened native workspace. Read and follow the file that exists.

## OpenClaw-Specific Delta

- Select repository skills through the `name` and `description` frontmatter in `skills/{name}/SKILL.md`.
- Resolve `COMFYUI_URL` and `COMFYUI_PATH` from the OpenClaw environment before falling back to repository session or inventory state.
- Use OpenClaw's available command and HTTP tools to execute the same inventory-first workflow defined by the canon.
- Treat `SOUL.md` and `TOOLS.md` as persona and tool adapters only; neither overrides the canonical `AGENT.md`.
