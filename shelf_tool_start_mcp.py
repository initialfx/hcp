# HCP — 서버 시작 쉘 툴
# 후디니 쉘 툴에 이 코드를 복사해서 넣으세요 (쉘 우클릭 → New Tool → Script 탭)
#
# 사전 요구 사항:
#   - hcp 패키지가 후디니의 Python 경로(Python path)에 포함되어 있어야 합니다.
#   - 설치 방법은 README.md를 참조하세요.
import sys
if "C:/HOU/Dev" not in sys.path:
    sys.path.append("C:/HOU/Dev")

import hou
import hcp

if hcp.is_server_running():
    server = hou.session.hcp_server
    hou.ui.displayMessage(f"HCP 서버가 이미 {server.host}:{server.port}에서 실행 중입니다.")
else:
    hcp.start_server()
    if hcp.is_server_running():
        server = hou.session.hcp_server
        hou.ui.displayMessage(f"HCP 서버가 {server.host}:{server.port}에서 시작되었습니다.")
    else:
        hou.ui.displayMessage("HCP 서버 시작에 실패했습니다.")

