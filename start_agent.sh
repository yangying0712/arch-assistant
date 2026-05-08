#!/bin/bash
cd /mnt/e/workspace/UserRegister/arch-assistant
set -a; source .env; set +a
exec uvicorn apps.agent-runtime.agent_runtime.main:app --host 0.0.0.0 --port 8003 2>&1
