# HCP — 서버 중지 쉘 툴
# 후디니 쉘 툴에 이 코드를 복사해서 넣으세요 (쉘 우클릭 → New Tool → Script 탭)
import sys
if "C:/HOU/Dev" not in sys.path:
    sys.path.append("C:/HOU/Dev")

import hou
import hcp

if hcp.is_server_running():
    hcp.stop_server()
    hou.ui.displayMessage("HCP 서버가 중지되었습니다.")
else:
    hou.ui.displayMessage("HCP 서버가 실행 중이 아닙니다.")

