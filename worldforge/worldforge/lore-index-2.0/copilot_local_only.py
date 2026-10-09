# Makes ComfyUI-Copilot chat run 100% local: no Alibaba MCP server, no ModelScope search.
# Backs up each file as <name>.orig before touching it. Run with ComfyUI closed.
import re, shutil, sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else r"D:\ComfyUI312\ComfyUI\custom_nodes\ComfyUI-Copilot")
mcp = root / "backend" / "service" / "mcp_client.py"
glb = root / "backend" / "utils" / "globals.py"

for f in (mcp, glb):
    b = f.with_suffix(f.suffix + ".orig")
    if not b.exists():
        shutil.copy2(f, b)

s = mcp.read_text(encoding="utf-8")

# 1. local tools in
s = s.replace(
    "from ..service.workflow_rewrite_tools import get_current_workflow\n",
    "from ..service.workflow_rewrite_tools import get_current_workflow, search_node_local, get_node_infos\n"
    "from ..service.parameter_tools import get_model_files\n", 1)

# 2. remote MCP servers out
s, n = re.subn(
    r"        # Create MCP server instances\n.*?        async with mcp_server, bing_server:\n",
    "        server_list = []\n        if True:\n",
    s, count=1, flags=re.S)
assert n == 1, "MCP server block not found"

# 3. route 'new workflow' requests to the local rewrite agent
s = s.replace(
    "            agent = create_agent(\n                name=\"ComfyUI-Copilot\",",
    "            workflow_creation_instruction = \"\"\"\n**CASE 3: CREATE NEW WORKFLOW**\n"
    "IF the user wants a NEW workflow or asks to build/generate one:\n"
    "- Action: handoff to the `Workflow Rewrite Agent` to build it on the current canvas.\n\"\"\"\n"
    "            workflow_constraint = \"\"\n\n"
    "            agent = create_agent(\n                name=\"ComfyUI-Copilot\",", 1)
s = re.sub(r"- If you cannot find the information needed.*?bing_search.*?\n", "", s)
s = re.sub(r"- If search_node tool cannot find the node, you MUST use bing_search.*?\n",
           "- To find nodes, use search_node_local and get_node_infos.\n", s)

# 4. give the chat agent the local tools
s = s.replace("                tools=[get_current_workflow],",
              "                tools=[get_current_workflow, search_node_local, get_node_infos, get_model_files],", 1)
mcp.write_text(s, encoding="utf-8")

# 5. any leftover default LLM URL points at Ollama, not Alibaba
g = glb.read_text(encoding="utf-8")
g = g.replace('LLM_DEFAULT_BASE_URL = "https://comfyui-copilot-server.onrender.com/v1"',
              'LLM_DEFAULT_BASE_URL = "http://localhost:11434/v1"', 1)
glb.write_text(g, encoding="utf-8")

compile(mcp.read_text(encoding="utf-8"), str(mcp), "exec")
print("Copilot is now local-only. Start ComfyUI.")
