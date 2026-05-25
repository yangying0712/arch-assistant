@echo off
setlocal
set "ROOT=%~dp0.."
cd /d "%ROOT%"

if not exist "%ROOT%\.venv-win\Scripts\python.exe" (
  echo Missing .venv-win. Run: python -m venv .venv-win
  exit /b 1
)

if exist "%ROOT%\.env" (
  for /f "usebackq tokens=1,* delims==" %%A in ("%ROOT%\.env") do (
    if not "%%A"=="" if not "%%A:~0,1%"=="#" set "%%A=%%B"
  )
)

set "LLM_ROUTER_HOST=http://127.0.0.1:8002"
set "AGENT_RUNTIME_HOST=http://127.0.0.1:8003"
set "ORCHESTRATION_HOST=http://127.0.0.1:8001"
set "FRONTEND_DIST=%ROOT%\frontend\dist"

start "arch-llm-router" cmd /k "cd /d "%ROOT%\apps\llm-router" && "%ROOT%\.venv-win\Scripts\python.exe" -m uvicorn llm_router.main:app --host 127.0.0.1 --port 8002"
start "arch-agent-runtime" cmd /k "cd /d "%ROOT%\apps\agent-runtime" && "%ROOT%\.venv-win\Scripts\python.exe" -m uvicorn agent_runtime.main:app --host 127.0.0.1 --port 8003"
start "arch-orchestration" cmd /k "cd /d "%ROOT%\apps\orchestration-engine" && "%ROOT%\.venv-win\Scripts\python.exe" -m uvicorn orchestration_engine.main:app --host 127.0.0.1 --port 8001"
start "arch-api-gateway" cmd /k "cd /d "%ROOT%\apps\api-gateway" && "%ROOT%\.venv-win\Scripts\python.exe" -m uvicorn api_gateway.main:app --host 127.0.0.1 --port 3000"

echo Started local service windows.
echo Open http://127.0.0.1:3000/
