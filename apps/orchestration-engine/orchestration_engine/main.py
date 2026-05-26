"""Orchestration Engine - 微服务编排引擎

完整流水线:
  User Input → classify_intent → agent_analysis → knowledge_retrieval → generate_report → response
"""
import os, json, time, asyncio, hashlib
from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from loguru import logger
from pydantic import BaseModel

# ── Config ─────────────────────────────────────────
LLM_ROUTER_URL = os.getenv("LLM_ROUTER_HOST", "http://localhost:8002")
AGENT_RUNTIME_URL = os.getenv("AGENT_RUNTIME_HOST", "http://localhost:8003")
CACHE_TTL = int(os.getenv("RESPONSE_CACHE_TTL", "300"))
CACHE_MAX = int(os.getenv("RESPONSE_CACHE_MAX", "500"))

_cache: dict[str, tuple[dict, float]] = {}  # (full_response, timestamp)

def _cache_key(prompt: str) -> str:
    return hashlib.sha256(prompt.strip().lower().encode()).hexdigest()

# ── Models ─────────────────────────────────────────
class PipelineRequest(BaseModel):
    prompt: str
    session_id: str = "default"

class StepInfo(BaseModel):
    name: str
    status: str
    output: dict | None = None

class PipelineResponse(BaseModel):
    session_id: str
    features: dict | None = None
    candidates: list | None = None
    report: str | None = None
    steps: list[StepInfo] = []
    cached: bool = False

# ── HTTP Client ────────────────────────────────────
client = httpx.AsyncClient(timeout=120.0)

async def call_with_retry(method: str, url: str, **kwargs) -> httpx.Response:
    for attempt in range(3):
        try:
            r = await client.request(method, url, **kwargs)
            if r.status_code < 500:
                return r
        except Exception as e:
            if attempt == 2:
                raise
            await asyncio.sleep(0.5 * (attempt + 1))
    raise HTTPException(status_code=502, detail="Upstream service unavailable")

# ── App ────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🎯 Architecture Orchestration Engine starting...")
    yield
    await client.aclose()

app = FastAPI(
    title="Architecture Recommendation Orchestration Engine",
    version="1.0.0",
    lifespan=lifespan,
)

@app.get("/health")
async def health():
    return {"service": "orchestration-engine", "status": "healthy"}

@app.post("/api/v1/analyze", response_model=PipelineResponse)
async def analyze(request: PipelineRequest):
    """运行完整的架构推荐流水线"""
    t0 = time.perf_counter()
    logger.info(f"📥 [{request.session_id}] 收到请求: {request.prompt[:80]}...")
    
    # 缓存检查
    key = _cache_key(request.prompt)
    if CACHE_TTL > 0 and key in _cache:
        cached_data, cached_ts = _cache[key]
        if time.time() - cached_ts < CACHE_TTL:
            logger.info("⚡ 缓存命中（完整响应）")
            return PipelineResponse(
                session_id=request.session_id,
                features=cached_data.get("features"),
                candidates=cached_data.get("candidates"),
                report=cached_data.get("report"),
                steps=[StepInfo(name="cache_hit", status="success")],
                cached=True,
            )
    
    steps = []
    
    # Step 1: 调用 Agent Runtime（三 Agent 协作）
    logger.info("🤖 调用 Agent Runtime...")
    try:
        r = await call_with_retry(
            "POST", f"{AGENT_RUNTIME_URL}/api/v1/run",
            json={"prompt": request.prompt, "session_id": request.session_id},
            timeout=180.0,
        )
        agent_result = r.json()
        steps.append(StepInfo(name="agent_analysis", status="success",
            output={"stage": agent_result.get("current_stage")}))
    except Exception as e:
        logger.error(f"Agent Runtime 调用失败: {e}")
        steps.append(StepInfo(name="agent_analysis", status="error"))
        raise HTTPException(status_code=500, detail=f"Agent analysis failed: {e}")
    
    features = agent_result.get("features")
    candidates = agent_result.get("candidates")
    report = agent_result.get("report")
    
    # Step 2: LLM 润色报告（可选）
    if report and LLM_ROUTER_URL:
        try:
            logger.info("✨ LLM 润色报告...")
            r = await call_with_retry(
                "POST", f"{LLM_ROUTER_URL}/api/v1/generate",
                json={
                    "messages": [
                        {"role": "system", "content": "你是一个软件架构报告编辑。请润色以下评估报告，使其更加专业和结构化。保持原有内容和结论不变。"},
                        {"role": "user", "content": report},
                    ],
                    "temperature": 0.2,
                },
                timeout=60.0,
            )
            polished = r.json().get("content", report)
            report = polished
            steps.append(StepInfo(name="report_polish", status="success"))
        except Exception as e:
            logger.warning(f"LLM 润色失败(非致命): {e}")
            steps.append(StepInfo(name="report_polish", status="skipped"))
    
    # 缓存完整响应
    if report and CACHE_TTL > 0:
        if len(_cache) >= CACHE_MAX:
            oldest = min(_cache, key=lambda k: _cache[k][1])
            _cache.pop(oldest, None)
        _cache[key] = ({"features": features, "candidates": candidates, "report": report}, time.time())
    
    elapsed = round((time.perf_counter() - t0) * 1000)
    logger.info(f"✅ [{request.session_id}] 流水线完成 ({elapsed}ms)")
    
    return PipelineResponse(
        session_id=request.session_id,
        features=features,
        candidates=candidates,
        report=report,
        steps=steps,
    )

@app.post("/api/v1/analyze/stream")
async def analyze_stream(request: PipelineRequest):
    """SSE 流式返回"""
    async def event_stream():
        yield f"data: {json.dumps({'event': 'status', 'message': '🤖 正在调用 Agent Runtime...'})}\n\n"
        
        try:
            async with httpx.AsyncClient() as stream_client:
                async with stream_client.stream(
                    "POST",
                    f"{AGENT_RUNTIME_URL}/api/v1/run/stream",
                    json={"prompt": request.prompt, "session_id": request.session_id},
                    timeout=180.0,
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line:
                            yield line + "\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'event': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")
