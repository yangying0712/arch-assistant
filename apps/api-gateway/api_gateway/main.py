"""API Gateway - 统一入口，路由请求到编排引擎"""
import os, json, asyncio
from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel

ORCHESTRATION_URL = os.getenv("ORCHESTRATION_HOST", "http://localhost:8001")
client = httpx.AsyncClient(timeout=180.0)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🌐 API Gateway starting...")
    yield
    await client.aclose()

app = FastAPI(title="Architecture Assistant API Gateway", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

APP_DIR = os.path.dirname(__file__)
LEGACY_HTML_PATH = os.path.join(APP_DIR, "templates", "index.html")
FRONTEND_DIST = os.getenv(
    "FRONTEND_DIST",
    os.path.abspath(os.path.join(APP_DIR, "..", "..", "..", "frontend", "dist")),
)
FRONTEND_INDEX = os.path.join(FRONTEND_DIST, "index.html")

if os.path.exists(os.path.join(FRONTEND_DIST, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="frontend-assets")

class AnalyzeRequest(BaseModel):
    prompt: str
    session_id: str = "default"

@app.get("/health")
async def health():
    return {"service": "api-gateway", "status": "healthy"}

@app.post("/api/v1/analyze")
async def analyze(req: AnalyzeRequest):
    """转发到编排引擎"""
    try:
        r = await client.post(
            f"{ORCHESTRATION_URL}/api/v1/analyze",
            json=req.model_dump(),
            timeout=180.0,
        )
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=r.text[:500])
        return r.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Orchestration engine unreachable: {e}")

@app.post("/api/v1/analyze/stream")
async def analyze_stream(req: AnalyzeRequest):
    """流式转发"""
    async def proxy():
        async with client.stream("POST", f"{ORCHESTRATION_URL}/api/v1/analyze/stream",
                                  json=req.model_dump(), timeout=180.0) as r:
            async for line in r.aiter_lines():
                if line:
                    yield line + "\n"
    return StreamingResponse(proxy(), media_type="text/event-stream")

@app.get("/")
async def home():
    """Serve the polished Vue frontend when built; fall back to the legacy demo."""
    if os.path.exists(FRONTEND_INDEX):
        return FileResponse(FRONTEND_INDEX)
    with open(LEGACY_HTML_PATH, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.get("/legacy", response_class=HTMLResponse)
async def legacy_home():
    """Keep the original single-file demo available for backup presentations."""
    with open(LEGACY_HTML_PATH, "r", encoding="utf-8") as f:
        return f.read()
