import hou
from .server import HcpServer

def start_server(host='127.0.0.1', port=9876):
    existing = getattr(hou.session, "hcp_server", None)
    if existing is not None and existing.running:
        print(f"HCP Server is already running on {existing.host}:{existing.port}")
        return
    if existing is not None and not existing.running:
        existing.stop()
    server = HcpServer(host=host, port=port)
    server.start()
    if server.running:
        hou.session.hcp_server = server
    else:
        hou.session.hcp_server = None

def stop_server():
    existing = getattr(hou.session, "hcp_server", None)
    if existing is not None:
        existing.stop()
        hou.session.hcp_server = None
    else:
        print("HCP Server is not running.")

def is_server_running():
    existing = getattr(hou.session, "hcp_server", None)
    return existing is not None and existing.running

def restart_server(host='127.0.0.1', port=9876):
    stop_server()
    start_server(host=host, port=port)

def initialize_plugin():
    if not hasattr(hou.session, "hcp_use_assetlib"):
        hou.session.hcp_use_assetlib = False
