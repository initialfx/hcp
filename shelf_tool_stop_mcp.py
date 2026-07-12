# HCP — Stop Server shelf tool
# Copy this into a Houdini shelf tool (right-click shelf → New Tool → Script tab)
import sys
if "C:/HOU/Dev" not in sys.path:
    sys.path.append("C:/HOU/Dev")

import hou
import hcp

if hcp.is_server_running():
    hcp.stop_server()
    hou.ui.displayMessage("HCP Server stopped")
else:
    hou.ui.displayMessage("HCP Server is not running")
