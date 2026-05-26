"""Agent Runtime - FastAPI service for running the multi-agent architecture recommendation pipeline."""
import os, sys, json, time, asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from loguru import logger
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(__file__))
from .graph import agent_graph, AgentState

# ── Models ─────────────────────────────────────────
class RunTaskRequest(BaseModel):
    prompt: str
    session_id: str = "default"
    metadata: dict | None = None

class RunTaskResponse(BaseModel):
    session_id: str
    features: dict | None = None
    candidates: list | None = None
    report: str | None = None
    current_stage: str
    elapsed_ms: float

# ── App ────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Architecture Agent Runtime starting...")
    yield
    logger.info("Agent Runtime shutting down")

app = FastAPI(
    title="Architecture Recommendation Agent Runtime",
    version="1.0.0",
    lifespan=lifespan,
    description="Multi-Agent system for software architecture style recommendation.",
)

@app.get("/health")
async def health():
    return {"service": "agent-runtime", "status": "healthy"}

@app.post("/api/v1/run", response_model=RunTaskResponse)
async def run_task(request: RunTaskRequest):
    """运行三 Agent 协作流水线"""
    t0 = time.perf_counter()
    logger.info(f"📥 Received task: {request.prompt[:80]}...")
    
    # 注入历史案例作为Few-shot上下文
    case_context = _build_case_context(request.prompt)
    if case_context:
        logger.info(f"📚 知识进化: 注入 {case_context.count(chr(10))} 行案例参考")
    
    state: AgentState = {
        "messages": [],
        "user_requirement": request.prompt,
        "extracted_features": {},
        "candidate_styles": [],
        "recommendations": [],
        "evaluation_report": "",
        "current_stage": "init",
        "next_step": "",
        "case_context": case_context,
    }
    
    try:
        result = await agent_graph.ainvoke(state)
    except Exception as e:
        logger.error(f"Agent pipeline failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    # 自动保存案例（知识进化）
    try:
        _save_case(
            request.prompt,
            result.get("extracted_features", {}),
            result.get("candidate_styles", []),
            result.get("evaluation_report", ""),
        )
    except Exception as e:
        logger.warning(f"案例保存失败(非致命): {e}")
    
    elapsed = round((time.perf_counter() - t0) * 1000)
    logger.info(f"✅ Pipeline complete in {elapsed}ms")
    
    return RunTaskResponse(
        session_id=request.session_id,
        features=result.get("extracted_features"),
        candidates=result.get("candidate_styles"),
        report=result.get("evaluation_report"),
        current_stage=result.get("current_stage", "unknown"),
        elapsed_ms=elapsed,
    )

@app.post("/api/v1/run/stream")
async def run_task_stream(request: RunTaskRequest):
    """SSE 流式返回 Agent 执行进度"""
    async def event_stream():
        case_context = _build_case_context(request.prompt)
        state: AgentState = {
            "messages": [],
            "user_requirement": request.prompt,
            "extracted_features": {},
            "candidate_styles": [],
            "recommendations": [],
            "evaluation_report": "",
            "current_stage": "init",
            "next_step": "",
            "case_context": case_context,
        }
        
        yield f"data: {json.dumps({'event': 'status', 'message': '🔍 正在分析需求...'})}\n\n"
        
        # Stream through graph steps manually
        try:
            async for event in agent_graph.astream(state):
                node_name = list(event.keys())[0] if event else "unknown"
                node_data = event.get(node_name, {})
                stage = node_data.get("current_stage", "")
                
                if "features" in stage:
                    feats = node_data.get("extracted_features", {})
                    yield f"data: {json.dumps({'event': 'features', 'data': feats})}\n\n"
                elif "matched" in stage:
                    cands = node_data.get("candidate_styles", [])
                    yield f"data: {json.dumps({'event': 'candidates', 'data': cands})}\n\n"
                elif "evaluation" in stage:
                    cands = node_data.get("candidate_styles", [])
                    yield f"data: {json.dumps({'event': 'candidates', 'data': cands})}\n\n"
                    report = node_data.get("evaluation_report", "")
                    yield f"data: {json.dumps({'event': 'report', 'data': report})}\n\n"

            yield f"data: {json.dumps({'event': 'done'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'event': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"},
    )

# ── Knowledge Evolution ─────────────────────────
CASES_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "learned_cases.json")

def _load_cases() -> list[dict]:
    if not os.path.exists(CASES_PATH):
        return []
    import json
    with open(CASES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_case(prompt: str, features: dict, candidates: list, report: str):
    """自动保存分析案例，用于知识进化"""
    cases = _load_cases()
    # 去重：相似prompt不重复存
    prompt_lower = prompt.strip().lower()
    for c in cases:
        if c.get("prompt", "").strip().lower() == prompt_lower:
            c["count"] = c.get("count", 1) + 1
            c["last_used"] = time.time()
            _write_cases(cases)
            return
    cases.append({
        "prompt": prompt,
        "features": features,
        "candidates": candidates,
        "report": report[:500],  # 截断存储
        "count": 1,
        "created": time.time(),
        "last_used": time.time(),
    })
    _write_cases(cases)

def _write_cases(cases: list):
    import json
    os.makedirs(os.path.dirname(CASES_PATH), exist_ok=True)
    with open(CASES_PATH, "w", encoding="utf-8") as f:
        json.dump(cases, f, ensure_ascii=False, indent=2)

def _build_case_context(prompt: str, max_cases: int = 3) -> str:
    """检索相似历史案例，生成Few-shot上下文"""
    cases = _load_cases()
    if not cases:
        return ""
    # 简单关键词匹配排序
    prompt_words = set(prompt.lower().split())
    scored = []
    for c in cases:
        case_words = set(c.get("prompt", "").lower().split())
        score = len(prompt_words & case_words)
        scored.append((score, c))
    scored.sort(key=lambda x: -x[0])
    
    lines = ["\n【历史成功案例（Few-shot参考）】"]
    for score, case in scored[:max_cases]:
        if score < 3:
            continue
        cand_names = [c.get("name", "?") for c in case.get("candidates", [])[:2]]
        lines.append(f"- 需求: {case['prompt'][:80]}... → 推荐: {' > '.join(cand_names)}")
    return "\n".join(lines) if len(lines) > 1 else ""

class KnowledgeEntry(BaseModel):
    name: str
    aliases: list[str] = []
    category: str = ""
    description: str = ""
    scalability: str = "中"
    performance: str = "中"
    coupling: str = "中"
    complexity: str = "中"
    deployability: str = "单体"
    testability: str = "中"
    适合场景: list[str] = []
    不适合场景: list[str] = []
    优点: list[str] = []
    缺点: list[str] = []
    关键技术: list[str] = []
    典型案例: list[str] = []

class FeedbackRequest(BaseModel):
    prompt: str
    session_id: str = ""
    rating: int = 5  # 1-5
    comment: str = ""

@app.get("/api/v1/knowledge")
async def list_knowledge():
    """列出所有架构风格"""
    from .graph import load_knowledge
    styles = load_knowledge()
    return {"total": len(styles), "styles": [{"name": s["name"], "category": s.get("category",""), "scalability": s.get("scalability",""), "complexity": s.get("complexity","")} for s in styles]}

@app.post("/api/v1/knowledge")
async def add_knowledge(entry: KnowledgeEntry):
    """添加新架构风格到知识库"""
    import json
    from .graph import KNOWLEDGE_PATH
    with open(KNOWLEDGE_PATH, "r", encoding="utf-8") as f:
        styles = json.load(f)
    
    # Check duplicate
    for s in styles:
        if s["name"] == entry.name:
            raise HTTPException(status_code=409, detail=f"架构 '{entry.name}' 已存在")
    
    styles.append(entry.model_dump())
    with open(KNOWLEDGE_PATH, "w", encoding="utf-8") as f:
        json.dump(styles, f, ensure_ascii=False, indent=2)
    
    logger.info(f"📚 知识进化: 新增架构风格 '{entry.name}'")
    return {"status": "added", "name": entry.name, "total": len(styles)}

# ── Case Library ─────────────────────────────
@app.get("/api/v1/cases")
async def list_cases():
    """列出历史学习案例"""
    cases = _load_cases()
    return {"total": len(cases), "cases": cases}

@app.get("/api/v1/cases/stats")
async def case_stats():
    """案例库统计"""
    cases = _load_cases()
    return {
        "total_cases": len(cases),
        "total_runs": sum(c.get("count", 1) for c in cases),
        "unique_domains": len({c.get("features", {}).get("domain", "") for c in cases if c.get("features", {}).get("domain")}),
    }

@app.post("/api/v1/cases")
async def add_case(feedback: FeedbackRequest):
    """手动提交案例反馈"""
    return {"status": "received", "prompt": feedback.prompt[:60], "rating": feedback.rating}
