# HCP — Start Server shelf tool
# Copy this into a Houdini shelf tool (right-click shelf → New Tool → Script tab)
#
# Prerequisites:
#   - hcp package must be in Houdini's Python path
#   - See README.md for setup instructions
import sys
if "C:/HOU/Dev" not in sys.path:
    sys.path.append("C:/HOU/Dev")

import hou
import hcp

if hcp.is_server_running():
    server = hou.session.hcp_server
    hou.ui.displayMessage(f"HCP Server is already running on {server.host}:{server.port}")
else:
    hcp.start_server()
    if hcp.is_server_running():
        server = hou.session.hcp_server
        hou.ui.displayMessage(f"HCP Server started on {server.host}:{server.port}")
    else:
        hou.ui.displayMessage("HCP Server failed to start")
