# HCP – Model Context Protocol을 통한 Houdini와 AI(Claude, Cursor, LM Studio) 연결

**HCP (Houdini Connection Protocol)**는 **Model Context Protocol (MCP)**을 통해 **Claude**, **Cursor**, **LM Studio** 등의 AI 도구에서 **SideFX Houdini**를 직접 제어할 수 있도록 돕는 도구입니다.

HCP는 다음 두 가지 컴포넌트로 구성됩니다:
1. **Houdini 플러그인 (Python 패키지)**: Houdini 내부에서 작동하며, 로컬 포트(기본값 `9876`)를 열고 AI의 명령(노드 생성, 파라미터 변경, 코드 실행 등)을 처리합니다.
2. **MCP 브릿지 서버 (`hcp_server.py`)**: AI 도구와 표준 입출력(stdin/stdout)으로 통신하고, Houdini와 TCP 소켓으로 통신하는 매개체입니다.

---

## 목차
1. [요구 사항](#요구-사항)
2. [1단계: Houdini HCP 플러그인 설치](#1단계-houdini-hcp-플러그인-설치)
3. [2단계: Python 및 uv 설치](#2단계-python-및-uv-설치)
4. [3단계: AI 도구 연동 (Cursor / LM Studio / Claude)](#3단계-ai-도구-연동-cursor--lm-studio--claude)
5. [4단계: 테스트 및 연결 확인](#4단계-테스트-및-연결-확인)
6. [OPUS API 연동 (선택사항)](#opus-api-연동-선택사항)
7. [문제 해결](#문제-해결)

---

## 요구 사항
- **SideFX Houdini** (Python 3 버전 포함)
- **uv** (빠른 Python 패키지 매니저)
- **Cursor**, **LM Studio**, 혹은 **Claude Desktop** 중 하나 이상의 AI 도구

---

## 1단계: Houdini HCP 플러그인 설치

### 1.1 폴더 배치
Houdini가 파이썬 패키지를 탐색할 수 있도록 아래 경로에 `hcp` 폴더를 복사하거나 링크합니다.
`C:/Users/<사용자명>/Documents/houdiniXX.X/scripts/python/hcp/`

**`hcp/` 폴더 내부 구성:**
- `__init__.py` – 플러그인 초기화 및 서버 시작/중지 함수 정의
- `server.py` – 포트 `9876`에서 대기하는 `HcpServer` 코어 로직
- `hcp_server.py` – MCP 브릿지 진입점
- `pyproject.toml` – 프로젝트 종속성 정의

### 1.2 쉘 툴(Shelf Tool) 등록
Houdini 내에서 서버를 편리하게 켜고 끌 수 있는 토글 버튼을 쉘에 추가합니다.

1. Houdini의 상단 쉘 바에서 **우클릭** → **"New Shelf..."** 클릭 후 이름을 `HCP`로 만듭니다.
2. 새로 만든 쉘에서 **우클릭** → **"New Tool..."**을 선택합니다.
   - **Name**: `toggle_hcp_server`
   - **Label**: `HCP`
3. **Script** 탭에 아래 코드를 입력합니다:
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

### 1.3 패키지 방식 자동 로드 (선택사항)
Houdini 실행 시 플러그인이 자동으로 로드되도록 하려면, Houdini 패키지 폴더(`C:/Users/<사용자명>/Documents/houdiniXX.X/packages/`)에 `hcp.json` 파일을 생성하고 아래 내용을 입력합니다.
```json
{
  "path": "$HOME/houdini20.5/scripts/python/hcp",
  "load_package_once": true,
  "version": "0.1",
  "env": [
    {
      "PYTHONPATH": "$PYTHONPATH;$HOME/houdini20.5/scripts/python"
    }
  ]
}
```

---

## 2단계: Python 및 `uv` 설치

HCP 브릿지는 고성능 패키지 매니저인 `uv`를 통해 실행됩니다.

```powershell
# 1) uv 설치 (Windows PowerShell 기준)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 2) uv 환경변수(PATH) 확인 및 패키지 설치
# 프로젝트 루트 디렉터리(c:\HOU\Dev\hcp)로 이동하여 실행
uv add "mcp[cli]"

# 3) MCP 라이브러리 정상 설치 확인
uv run python -c "import mcp.server.fastmcp; print('MCP가 정상적으로 설치되었습니다!')"
```

---

## 3단계: AI 도구 연동 (Cursor / LM Studio / Claude)

Hcp 서버와 연동하여 AI가 Houdini를 조작하게 하려면, 각 AI 편집기에 MCP 서버 설정을 등록해야 합니다.

### 3.1 💻 Cursor 연동 방법 (추천)
**Cursor**는 코딩과 동시에 실시간으로 Houdini에 노드를 생성하고 수정할 수 있는 가장 강력한 환경을 제공합니다.

1. **Cursor 설정 열기**: Cursor 실행 후 우측 상단의 톱니바퀴 아이콘을 누르거나 `Ctrl + Shift + J` (Windows)를 눌러 **Settings**로 이동합니다.
2. **MCP 설정 탭 이동**: `Features` -> `MCP` 항목으로 이동합니다.
3. **서버 추가**: **`+ Add New MCP Server`** 버튼을 클릭합니다.
4. **설정값 입력**:
   - **Name**: `hcp`
   - **Type**: `command`
   - **Command**:
     ```bash
     uv --directory "C:\HOU\Dev\hcp" run hcp_server.py
     ```
     *(또는 `uv`의 절대 경로를 직접 적어주셔도 좋습니다. 예: `C:\Users\<사용자명>\AppData\Local\hermes\bin\uv.exe --directory "C:\HOU\Dev\hcp" run hcp_server.py`)*
5. **저장 및 확인**: `Save`를 누르면 하단에 초록색 동그라미와 함께 `hcp` 서버가 활성화된 것을 확인할 수 있습니다.

---

### 3.2 🤖 LM Studio 연동 방법 (로컬 LLM)
로컬에 구축된 대규모 언어 모델(LLM)을 사용할 때 **LM Studio**의 MCP 연동 기능을 이용할 수 있습니다.

LM Studio의 MCP 환경 설정 파일(`C:\Users\<사용자명>\.lmstudio\mcp.json`)에 아래와 같이 `hcp` 서버 설정을 직접 작성하거나 추가합니다:

```json
{
  "mcpServers": {
    "hcp": {
      "command": "C:\\Users\\<사용자명>\\AppData\\Local\\hermes\\bin\\uv.exe",
      "args": [
        "run",
        "hcp_server.py"
      ],
      "cwd": "C:\\HOU\\Dev\\hcp"
    }
  }
}
```
*주의: JSON 설정 파일 내 경로의 백슬래시(`\`)는 반드시 이중 백슬래시(`\\`)로 작성해야 합니다.*

---

### 3.3 💬 Claude Desktop 연동 방법
공식 Claude Desktop 앱을 사용하는 경우, 아래 경로의 설정 파일을 수정하여 연동합니다.

- 설정 파일 경로: `C:\Users\<사용자명>\AppData\Roaming\Claude\claude_desktop_config.json`
- 다음 내용을 추가합니다:

```json
{
  "mcpServers": {
    "hcp": {
      "command": "uv",
      "args": [
        "run",
        "hcp_server.py"
      ],
      "cwd": "C:/HOU/Dev/hcp"
    }
  }
}
```

---

## 4단계: 테스트 및 연결 확인

1. **Houdini 실행**: Houdini를 실행합니다.
2. **서버 구동**: 미리 만들어 둔 쉘 툴(HCP) 버튼을 클릭하여 `HcpServer started on localhost:9876` 메시지를 확인합니다.
3. **연결 테스트 스크립트 실행**:
   ```powershell
   python scratch/test_connection.py
   ```
   성공적으로 연결되면 `Connection test PASSED!` 라는 축하 메시지가 출력됩니다.
4. **AI 도구에서 명령 내리기**:
   Cursor나 Claude 채팅창에서 다음과 같이 한글로 요청해 보세요:
   > *"Houdini에 지오메트리 컨테이너를 만들고 그 안에 토러스(Torus)와 마운틴(Mountain SOP) 노드를 생성해서 연결해줘"*

---

## OPUS API 연동 (선택사항)

OPUS는 절차적 가구 및 환경 에셋을 임포트하는 기능을 제공합니다.
1. [RapidAPI](https://rapidapi.com/) 회원가입 후 [OPUS API](https://rapidapi.com/genel-gi78OM1rB/api/opus5)를 구독합니다.
2. `urls.env.example` 파일을 복사하여 `urls.env`로 이름을 변경합니다.
3. `urls.env` 파일 안에 본인의 Rapid API Key를 입력합니다. (이 파일은 `.gitignore`에 의해 보호됩니다.)
4. API 키가 없어도 HCP 서버의 다른 기능은 정상적으로 작동합니다.
