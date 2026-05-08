"""Agent Runtime - 基于 LangGraph 的三 Agent 协作系统

三个 Agent 的分工：
- RequirementAnalysisAgent: 需求解析 - 从自然语言中提取架构关键特征
- ArchitectureMatchingAgent: 架构匹配 - 将特征与知识库中的架构风格匹配
- EvaluationAgent: 评估生成 - 多维度对比分析，生成推荐报告
"""
import json, re, os
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from loguru import logger
KNOWLEDGE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "architecture_styles.json")

# ── State ──────────────────────────────────────────
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    user_requirement: str
    extracted_features: dict
    candidate_styles: list
    recommendations: list
    evaluation_report: str
    current_stage: str
    next_step: str
    case_context: str  # 知识进化：历史案例Few-shot上下文

# ── LLM ────────────────────────────────────────────
llm = ChatOpenAI(
    model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
    api_key=os.getenv("DEEPSEEK_API_KEY", ""),
    base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
    temperature=0.3,
    max_tokens=2048,
)

# ── Knowledge Base ─────────────────────────────────
def load_knowledge() -> list[dict]:
    with open(KNOWLEDGE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def build_knowledge_summary() -> str:
    """构建增强的知识摘要 — 为每种架构标注强信号关键词和禁止信号"""
    styles = load_knowledge()
    lines = []
    for s in styles:
        name = s['name']
        category = s.get('category', '')
        desc = s.get('description', '')
        
        # 构建强信号（触发该架构的关键词）
        signals = {
            "分层架构 (Layered Architecture)": "分层/三层/n-tier/单体/简单业务/小团队",
            "微服务架构 (Microservices Architecture)": "微服务/独立部署/多团队/技术栈多样性/持续交付",
            "事件驱动架构 (Event-Driven Architecture)": "事件/消息/异步/实时/Kafka/削峰/解耦",
            "CQRS (命令查询职责分离)": "读写分离/CQRS/命令查询/读写负载差异/事件溯源/复杂查询报表/版本历史/冲突解决/Feed/推送/同步/审计/银行/交易/转账/一致性/事务",
            "管道-过滤器架构 (Pipe-Filter Architecture)": "管道/流水线/pipeline/过滤器/ETL/数据流/编译器/音视频处理/日志处理/数据转换",
            "SOA (面向服务架构)": "SOA/ESB/企业集成/遗留系统/异构系统/企业服务总线/WebService",
            "六边形架构/端口适配器 (Hexagonal/Ports & Adapters)": "六边形/端口适配器/DDD/可测试性/核心业务/依赖反转/替换外部/防腐层/外部系统对接/流程引擎/保险/理赔/审计追溯",
            "MVC架构 (Model-View-Controller)": "MVC/Web应用/博客/CMS/单体/快速开发/个人项目",
            "Space-Based架构 (基于空间的架构)": "高频交易/秒杀/极低延迟/空间架构/内存网格/实时竞价/游戏服务器",
            "对等架构 (Peer-to-Peer Architecture)": "P2P/去中心化/点对点/区块链/文件共享/无中心/BitTorrent/IPFS/节点对等/CDN/内容分发/边缘节点/就近/全球部署/智能缓存",
            "Serverless架构": "Serverless/无服务器/函数计算/FaaS/Lambda/按需/定时/凌晨/报表/日报/无需运维/突发/事件触发/拉取数据",
            "插件架构/微内核 (Plugin/Microkernel Architecture)": "插件/模块化/IDE/可扩展平台/微内核/OSGi/SPI/第三方扩展/产品化/API网关/路由/中间件/限流/认证/拦截器/协议转换",
        }
        
        anti_signals = {
            "分层架构 (Layered Architecture)": "微服务/分布式/高并发/独立部署",
            "微服务架构 (Microservices Architecture)": "小项目/个人/简单/单体/快速原型/低成本",
            "事件驱动架构 (Event-Driven Architecture)": "简单CRUD/强一致性事务/同步请求响应",
            "CQRS (命令查询职责分离)": "简单CRUD/业务逻辑极少/无查询需求",
            "管道-过滤器架构 (Pipe-Filter Architecture)": "交互式/请求响应/Web应用/电商",
            "SOA (面向服务架构)": "新系统/敏捷/微服务/初创/快速迭代",
            "六边形架构/端口适配器 (Hexagonal/Ports & Adapters)": "简单CRUD/快速原型/DDD不熟悉",
            "MVC架构 (Model-View-Controller)": "分布式/微服务/高并发/独立部署/多团队",
            "Space-Based架构 (基于空间的架构)": "小规模/简单/低并发/运维能力弱/团队小",
            "对等架构 (Peer-to-Peer Architecture)": "中央控制/强一致性/合规监管/事务",
            "Serverless架构": "长时间运行/有状态/精细控制/延迟敏感实时系统",
            "插件架构/微内核 (Plugin/Microkernel Architecture)": "简单应用/不需扩展/实时系统/一次性项目",
        }
        
        sig = signals.get(name, "")
        anti = anti_signals.get(name, "")
        
        lines.append(
            f"- {name} [{category}] | {desc[:60]}... | "
            f"触发词: {sig} | "
            f"排除词: {anti} | "
            f"可扩展: {s['scalability']} | 复杂度: {s['complexity']}"
        )
    return "\n".join(lines)

# ── Step 1: Requirement Analysis Agent ─────────────
REQUIREMENT_ANALYSIS_PROMPT = """你是一个软件架构需求分析师。从用户描述中提取架构关键特征。
输出严格JSON格式，不要markdown代码块：

{
  "domain": "应用领域",
  "features": ["特征1", "特征2", ...],
  "constraints": {
    "concurrency": "低/中/高/极高",
    "consistency": "低/中/高",
    "scalability_need": "低/中/高/极高",
    "complexity_tolerance": "低/中/高",
    "deployment_flexibility": "单体/独立/混合"
  },
  "key_requirements": ["关键非功能需求1", ...]
}

提取规则：
- concurrency: 提到"万人/百万/高并发/秒杀"→极高，"千级/中等"→中，"少量/个人"→低
- consistency: 提到"交易/支付/一致性/事务"→高，"最终一致"→中，"不要求"→低
- scalability_need: 提到"扩展/快速/大促/暴涨"→极高或高，"稳定/固定"→低
- complexity_tolerance: 提到"简单/快速/小团队"→低，"复杂/企业"→高
"""

async def requirement_analysis(state: AgentState) -> AgentState:
    logger.info("🔍 [需求解析Agent] 开始分析需求...")
    requirement = state["user_requirement"]
    messages = [
        SystemMessage(content=REQUIREMENT_ANALYSIS_PROMPT),
        HumanMessage(content=requirement),
    ]
    response = await llm.ainvoke(messages)
    try:
        result = json.loads(response.content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip())
    except json.JSONDecodeError:
        result = {"features": [], "constraints": {}, "key_requirements": []}
    
    state["extracted_features"] = result
    state["current_stage"] = "features_extracted"
    logger.info(f"   提取特征: {json.dumps(result, ensure_ascii=False)[:200]}")
    return state

# ── Step 2: Architecture Matching Agent ────────────
ARCHITECTURE_MATCHING_PROMPT = """你是一个软件架构匹配专家。根据需求特征推荐最匹配的3种候选架构风格。

⚠️ 核心原则（必须遵守）：
1. 每类架构各有适用场景，不存在"万能架构"。微服务和事件驱动并非默认最优解
2. 优先根据【触发词】匹配 — 需求中出现某架构的触发词时，该架构应排第一
3. 同时检查【排除词】— 需求中出现某架构的排除词时，不应推荐该架构
4. 简单项目（低并发/低复杂度/小团队/个人项目）优先推荐 MVC/分层/管道/Serverless，微服务得分应明显低于简单架构
5. 去中心化/P2P/区块链场景必须优先推荐对等架构，不得用事件驱动替代
6. 插件/可扩展平台/IDE/模块化产品场景必须优先推荐插件架构
7. 数据流/ETL/编译器/管道/音视频处理场景必须优先推荐管道-过滤器
8. 企业集成/遗留系统/ESB/SOAP场景必须优先推荐 SOA
9. Serverless适合事件触发/定时任务/突发负载/函数级任务，不适合长时间运行/有状态/实时系统
10. Space-Based适合极高高并发+极低延迟（秒杀/高频交易/游戏服务器），一般高并发用事件驱动即可
11. CDN/内容分发/边缘节点/就近获取/全球部署/缓存分发场景必须优先推荐对等架构，不得用事件驱动或微服务替代
12. 文件同步/版本历史/冲突解决/离线编辑场景必须优先推荐 CQRS + 事件溯源
13. 多独立业务模块且各自有不同扩展需求（如课程/考试/直播/作业）时，应合理推荐微服务架构
14. 保险理赔/核心业务复杂/对接多个外部系统/审计追溯场景必须优先推荐六边形架构
15. Feed流/社交媒体动态推送/关注关系/聚合推送场景必须优先推荐 CQRS + 事件驱动
16. API网关/路由转发/中间件链/协议转换/限流/认证鉴权场景必须优先推荐插件架构，不得被"微服务"关键词误导
17. 银行核心交易/转账/存款/贷款等强一致性+高并发场景必须优先推荐 CQRS 架构，事件驱动不满足强事务一致性要求
18. 定时报表/凌晨调度/按需执行/无需常驻服务器场景必须优先推荐 Serverless 架构，管道-过滤器仅作为数据处理子模式

可用架构风格知识库（含触发词和排除词）：
{knowledge_base}

用户需求特征：
{features}

请严格按上述原则推荐3种候选架构风格。输出严格JSON（不要markdown代码块）：
{{
  "candidates": [
    {{
      "name": "架构名称（必须与知识库中的name完全一致）",
      "match_score": 0.0-1.0,
      "match_reasons": ["理由1", "理由2"],
      "risks": ["风险1", "风险2"]
    }}
  ]
}}"""

async def architecture_matching(state: AgentState) -> AgentState:
    logger.info("🎯 [架构匹配Agent] 开始匹配...")
    features = state["extracted_features"]
    knowledge = build_knowledge_summary()
    requirement = state["user_requirement"]
    
    prompt = ARCHITECTURE_MATCHING_PROMPT.format(
        knowledge_base=knowledge,
        features=json.dumps(features, ensure_ascii=False, indent=2)
    )
    # 注入知识进化：历史案例作为Few-shot参考
    case_context = state.get("case_context", "")
    if case_context:
        prompt += case_context
    
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content="请严格根据需求特征和触发词/排除词规则，推荐最匹配的3种架构风格。不要陷入微服务/事件驱动的惯性思维。"),
    ]
    response = await llm.ainvoke(messages)
    try:
        result = json.loads(response.content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip())
        candidates = result.get("candidates", [])
    except json.JSONDecodeError:
        candidates = []
    
    state["candidate_styles"] = candidates
    state["current_stage"] = "styles_matched"
    logger.info(f"   匹配结果: {[c.get('name', '?') for c in candidates]}")
    return state

# ── Step 3 & 4: Rule Engine Validation ─────────────
def rule_engine_validate(candidates: list[dict], features: dict, requirement: str = "") -> list[dict]:
    """规则引擎：负面过滤 + 正向加分"""
    constraints = features.get("constraints", {})
    concurrency = constraints.get("concurrency", "中")
    req_lower = requirement.lower()
    
    full_kb = {s["name"]: s for s in load_knowledge()}
    
    # ── 正向加分规则：需求关键词触发小众架构加分 ──
    promotion_rules = [
        # 管道-过滤器触发词
        (["管道-过滤器"], ["管道", "pipeline", "流水线", "过滤器", "ETL", "数据流", "编译器", "音视频", "转码", "日志处理", "数据清洗", "数据转换", "数据聚合", "拉取数据"], 0.25),
        # 对等架构触发词（加强权重）
        (["对等架构"], ["P2P", "去中心化", "点对点", "区块链", "文件共享", "无中心", "BitTorrent", "IPFS", "节点对等", "无服务器节点", "CDN", "内容分发", "边缘节点", "就近", "全球部署", "缓存", "智能缓存"], 0.35),
        # Space-Based触发词
        (["Space-Based"], ["秒杀", "高频交易", "极低延迟", "内存网格", "实时竞价", "游戏服务器", "毫秒级", "空间架构"], 0.30),
        # Serverless触发词（定时任务场景大幅加分）
        (["Serverless"], ["Serverless", "无服务器", "函数计算", "FaaS", "Lambda", "按需付费", "定时", "cron", "调度", "凌晨", "日报", "周报", "无需运维", "突发流量", "事件触发", "Webhook"], 0.35),
        # 插件架构触发词（加强权重）
        (["插件"], ["插件", "IDE", "可扩展平台", "微内核", "OSGi", "SPI", "第三方扩展", "产品化", "模块化平台", "多租户SaaS", "API网关", "路由转发", "可插拔", "拦截器", "中间件链", "协议转换", "限流", "认证鉴权", "日志监控"], 0.30),
        # SOA触发词
        (["SOA"], ["SOA", "ESB", "企业集成", "遗留系统", "异构系统", "企业服务总线", "WebService", "SOAP", "电子政务", "跨部门", "统一办事"], 0.30),
        # CQRS触发词（加大权重）
        (["CQRS"], ["CQRS", "读写分离", "事件溯源", "命令查询", "读写负载差异", "复杂查询", "报表系统", "审计", "银行交易", "银行核心", "银行", "转账", "存款", "贷款", "一致性", "事务", "版本历史", "Feed流", "聚合推送", "动态推送", "冲突解决", "文件同步", "离线编辑"], 0.35),
        # 六边形触发词（加强权重）
        (["六边形"], ["六边形", "端口适配器", "DDD", "领域驱动", "防腐层", "依赖反转", "可测试性优先", "核心业务复杂", "保险", "理赔", "对接外部", "审计追溯", "对接多个外部", "报案", "查勘", "定损", "理算", "支付全流程"], 0.30),
    ]
    
    # 构建候选名称到架构的映射
    candidate_map = {}
    for c in candidates:
        name = c.get("name", "")
        for kb_name in full_kb:
            if kb_name in name or name in kb_name:
                candidate_map[kb_name] = c
                break
    
    # 应用正向加分
    for kb_names, keywords, boost in promotion_rules:
        if any(kw.lower() in req_lower for kw in keywords):
            for kb_name in kb_names:
                for cand_name, cand in candidate_map.items():
                    if kb_name in cand_name:
                        old_score = cand.get("match_score", 0.5)
                        cand["match_score"] = min(1.0, old_score + boost)
                        cand["rule_engine_note"] = f"关键词触发加分 +{boost:.0%}"
                        logger.info(f"   规则引擎加分: {cand_name} +{boost:.0%} (关键词匹配)")
                        break
    
    # ── 负面过滤规则 ──
    validated = []
    for c in candidates:
        name = c.get("name", "")
        kb = None
        for kb_name in full_kb:
            if kb_name in name or name in kb_name:
                kb = full_kb[kb_name]
                break
        
        if not kb:
            validated.append(c)
            continue
        
        # 规则1: 高并发场景惩罚低可扩展性架构
        if concurrency in ("高", "极高") and kb.get("scalability") in ("低",):
            logger.warning(f"   规则引擎降权: {name} 不适合高并发场景")
            if not c.get("rule_engine_note"):
                c["rule_engine_note"] = "不适合高并发场景"
            c["match_score"] = min(c.get("match_score", 0.5), 0.3)
        
        # 规则2: 简单项目惩罚高复杂度架构
        if constraints.get("complexity_tolerance") == "低" and kb.get("complexity") in ("高", "极高"):
            logger.warning(f"   规则引擎降权: {name} 复杂度过高")
            if not c.get("rule_engine_note"):
                c["rule_engine_note"] = "实现复杂度偏高"
            c["match_score"] = min(c.get("match_score", 0.5), 0.5)
        
        validated.append(c)
    
    # 按分数重新排序
    validated.sort(key=lambda c: c.get("match_score", 0), reverse=True)
    
    return validated

# ── Step 4: Evaluation Agent ───────────────────────
EVALUATION_PROMPT = """你是一个软件架构评估专家。基于候选架构风格进行多维度对比分析。

候选架构及匹配分数：
{candidates}

用户需求：
{requirement}

请生成一份专业评估报告，需包含以下部分（用中文）：

## 一、多维度对比分析
从 可扩展性、性能、实现复杂度、部署难度、团队要求 五个维度对比各候选架构。

## 二、架构影响溯源
对排名第一的推荐架构，追溯分析：用户需求中的哪些具体特征导致了这个推荐（至少3条因果链，格式："需求特征X → 架构选择Y → 原因Z"）

## 三、组合建议（如适用）
如果有两种架构可以优势互补，给出组合推荐方案（如 微服务+CQRS+事件驱动），并说明组合的优势

## 四、最终推荐及理由
明确推荐结果、核心理由和适用条件

## 五、优缺点总结
- 优点
- 缺点/风险（至少2条风险管理建议）"""

async def evaluation(state: AgentState) -> AgentState:
    logger.info("📊 [评估Agent] 生成评估报告...")
    
    # 先用规则引擎过滤（含正向加分）
    validated = rule_engine_validate(state["candidate_styles"], state["extracted_features"], state["user_requirement"])
    state["candidate_styles"] = validated
    
    messages = [
        SystemMessage(content=EVALUATION_PROMPT.format(
            candidates=json.dumps(validated, ensure_ascii=False, indent=2),
            requirement=state["user_requirement"]
        )),
        HumanMessage(content="请生成架构评估与推荐报告。"),
    ]
    response = await llm.ainvoke(messages)
    
    state["evaluation_report"] = response.content
    state["current_stage"] = "evaluation_complete"
    logger.info("   评估报告生成完成")
    return state

# ── Build Graph ────────────────────────────────────
def build_agent_graph() -> StateGraph:
    workflow = StateGraph(AgentState)
    
    workflow.add_node("requirement_analysis", requirement_analysis)
    workflow.add_node("architecture_matching", architecture_matching)
    workflow.add_node("evaluation", evaluation)
    
    workflow.set_entry_point("requirement_analysis")
    workflow.add_edge("requirement_analysis", "architecture_matching")
    workflow.add_edge("architecture_matching", "evaluation")
    workflow.add_edge("evaluation", END)
    
    return workflow.compile()

agent_graph = build_agent_graph()
