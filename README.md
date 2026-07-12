# HCP – Connect Houdini to Claude via Model Context Protocol

**HCP** allows you to control **SideFX Houdini** from **Claude** using the **Model Context Protocol (MCP)**. It consists of:

1. A **Houdini plugin** (Python package) that listens on a local port (default `localhost:9876`) and handles commands (creating and modifying nodes, executing code, etc.).  
2. An **MCP bridge script** you run via **uv** (or system Python) that communicates via **std**in/**std**out with Claude and **TCP** with Houdini.

Below are the complete instructions for setting up Houdini, uv, and Claude Desktop.

---

## Table of Contents

1. [Requirements](#requirements)  
2. [Houdini HCP Plugin Installation](#houdini-hcp-plugin-installation)  
   1. [Folder Layout](#folder-layout)  
   2. [Shelf Tool (Optional)](#shelf-tool-optional)  
   3. [Packages Integration (Optional)](#packages-integration-optional)  
3. [Installing the `mcp` Python Package](#installing-the-mcp-python-package)  
   1. [Using uv on Windows](#using-uv-on-windows)  
   2. [Using pip Directly](#using-pip-directly)  
4. [Bridging Script and Claude for Desktop](#bridging-script-and-claude-for-desktop)  
   1. [The Bridging Script](#the-bridging-script)  
   2. [Telling Claude Desktop to Use Your Script](#telling-claude-desktop-to-use-your-script)  
5. [Testing & Usage](#testing--usage)  
6. [Troubleshooting](#troubleshooting)

---

## Requirements

- **SideFX Houdini**  
- **uv** 
- **Claude Desktop** (latest version)

---

## 1. Houdini HCP Plugin Installation

### 1.1 Folder Layout

Create a folder in your Houdini scripts directory:
C:/Users/YourUserName/Documents/houdini19.5/scripts/python/hcp/

Inside **`hcp/`**, place:

- **`__init__.py`** – handles plugin initialization (start/stop server)  
- **`server.py`** – defines the `HcpServer` (listening on port `9876`)  
- **`hcp_server.py`** – optional bridging script (some prefer a separate location)
- **`pyproject.toml`**


*(If you prefer, `hcp_server.py` can live elsewhere. As long as you know its path for running with `uv`.)*

### 1.2 Shelf Tool 

create a **Shelf Tool** to toggle the server in Houdini:

1. **Right-click** a shelf → **"New Shelf..."** 

Name it "HCP" or something similar

2. **Right-click** again → **"New Tool..."** 
Name: "Toggle HCP Server"
Label: "HCP"

3. Under **Script**, insert something like:

```python
   import hou
   import hcp

   if hasattr(hou.session, "hcp_server") and hou.session.hcp_server:
       hcp.stop_server()
       hou.ui.displayMessage("HCP Server stopped")
   else:
       hcp.start_server()
       hou.ui.displayMessage("HCP Server started on localhost:9876")

```


### 1.3 Packages Integration 

If you want Houdini to auto-load your plugin at startup, create a package file named hcp.json in the Houdini packages folder (e.g. C:/Users/YourUserName/Documents/houdini19.5/packages/):
```json
{
  "path": "$HOME/houdini19.5/scripts/python/hcp",
  "load_package_once": true,
  "version": "0.1",
  "env": [
    {
      "PYTHONPATH": "$PYTHONPATH;$HOME/houdini19.5/scripts/python"
    }
  ]
}
```

### 2 Using uv on Windows
```powershell
  # 1) Install uv 
  powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

  # 2) add uv to your PATH (depends on the user instructions) from cmd
  set Path=C:\Users\<YourUserName>\.local\bin;%Path%

  # 3) In a uv project or the plugin directory
  cd C:/Users/<YourUserName>/Documents/houdini19.5/scripts/python/hcp/
  uv add "mcp[cli]"

  # 4) Verify
  uv run python -c "import mcp.server.fastmcp; print('MCP is installed!')"
```
### 3 Telling Claude for Desktop to Use Your Script
Go to File > Settings > Developer > Edit Config > 
Open or create:
claude_desktop_config.json

Add an entry:

```json
{
  "mcpServers": {
    "hcp": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "C:/Users/<YourUserName>/Documents/houdini19.5/scripts/python/hcp/hcp_server.py"
      ]
    }
  }
}
```
if uv run was successful and claude failed to load mcp, make sure claude is using the same python version, use:
```cmd
  python -c "import sys; print(sys.executable)"
``` 
to find python, and replace "python" with the path you got. 

### 4 Use Cursor / LM Studio
Go to Settings > MCP > add new MCP server
add the same entry in claude_desktop_config.json
you might need to stop claude and restart houdini and the server

### 5 OPUS integration

OPUS provide a large set of furniture and environmental procedural assets.
you will need a Rapid API key to log in. Create an account at: [RapidAPI](https://rapidapi.com/)
Subscribe to OPUS API at: [OPUS API Subscribe](https://rapidapi.com/genel-gi78OM1rB/api/opus5/pricing)
Get your Rapid API key at [OPUS API](https://rapidapi.com/genel-gi78OM1rB/api/opus5)
copy `urls.env.example` to `urls.env` and add your key (the file is gitignored).
OPUS integration is optional — without a key the server still starts, only the OPUS tools are disabled.
### 6 Acknowledgement

HCP was built following [blender-mcp](https://github.com/ahujasid/blender-mcp). We thank them for the contribution.
