"""Agent Runtime - 基于 LangGraph 的三 Agent 协作系统

三个 Agent 的分工：
- RequirementAnalysisAgent: 需求解析 - 从自然语言中提取架构关键特征
- ArchitectureMatchingAgent: 架构匹配 - 将特征与知识库中的架构风格匹配
- EvaluationAgent: 评估生成 - 多维度对比分析，生成推荐报告

知识库支持: Neo4j 图数据库 (优先) + JSON 文件 (fallback)
"""
import json, re, os
from datetime import date
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from loguru import logger
from .neo4j_kb import Neo4jKnowledgeBase  # Neo4j 图数据库查询

KNOWLEDGE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "architecture_styles.json")

# 全局 Neo4j 知识库实例（单例）
_neo4j_kb: Neo4jKnowledgeBase | None = None

def get_neo4j_kb() -> Neo4jKnowledgeBase:
    global _neo4j_kb
    if _neo4j_kb is None:
        _neo4j_kb = Neo4jKnowledgeBase()
    return _neo4j_kb

# ── State ──────────────────────────────────────────
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    user_requirement: str
    extracted_features: dict
    candidate_styles: list
    recommendations: list
    evaluation_report: str
    topology: dict
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
    """构建增强的知识摘要 — 优先 Neo4j 图查询，fallback JSON"""
    kb = get_neo4j_kb()
    if kb.is_available():
        # 使用 Neo4j 图数据库上下文
        neo4j_summary = kb.get_all_styles_summary()
        if neo4j_summary:
            lines = []
            for s in neo4j_summary:
                kws = ', '.join(s.get('keywords', [])[:4])
                antis = ', '.join(s.get('anti_keywords', [])[:3])
                pros = ', '.join(s.get('pros', [])[:2])
                cons = ', '.join(s.get('cons', [])[:2])
                lines.append(
                    f"- {s['name']} [{s.get('category','')}] | "
                    f"触发词: {kws} | 排除词: {antis} | "
                    f"优点: {pros} | 缺点: {cons}"
                )
            logger.info("📊 使用 Neo4j 知识图谱 ({} 种架构)", len(lines))
            return "\n".join(lines)

    # Fallback: JSON 知识库
    logger.info("📄 Neo4j 不可用，使用 JSON 知识库")
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
            "批处理架构 (Batch Processing Architecture)": "批处理/batch/离线/日终/清算/对账/监管报表/批量作业/可重跑/检查点/高吞吐",
            "主程序-子过程架构 (Main Program-Subroutine Architecture)": "主程序/子过程/main subroutine/过程式/命令行工具/固定流程/本地工具/简单稳定",
            "面向对象架构 (Object-Oriented Architecture)": "面向对象/object oriented/OO/类/对象/封装/继承/多态/图形对象/撤销重做/领域对象",
            "仓库架构 (Repository Architecture)": "仓库/repository/共享数据/统一知识库/中央数据存储/多工具集成/元数据/主数据",
            "黑板架构 (Blackboard Architecture)": "黑板/blackboard/共享工作区/知识源/多模型/增量推理/协同诊断/共享状态",
            "解释器架构 (Interpreter Architecture)": "解释器/interpreter/DSL/脚本/运行时解析/脚本引擎/模板/字节码/虚拟机",
            "规则系统架构 (Rule-Based System Architecture)": "规则系统/rule based/规则引擎/推理机/事实库/规则库/审批/风控/可解释决策",
            "进程通信架构 (Communicating Processes Architecture)": "进程通信/communicating processes/IPC/多进程/Socket/RPC/消息通道/调度进程/工作进程",
            "多Agent架构 (Multi-Agent Architecture)": "多Agent/multi-agent/智能体协作/规划Agent/检索Agent/评审Agent/协调Agent/共享记忆/任务分解",
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
            "批处理架构 (Batch Processing Architecture)": "实时交互/毫秒级响应/同步请求响应/人工频繁干预",
            "主程序-子过程架构 (Main Program-Subroutine Architecture)": "大型分布式/多团队/频繁扩展/复杂领域模型",
            "面向对象架构 (Object-Oriented Architecture)": "纯数据流水线/极简脚本/无状态批处理",
            "仓库架构 (Repository Architecture)": "去中心化/点对点/低延迟直连/写冲突极高",
            "黑板架构 (Blackboard Architecture)": "简单CRUD/严格线性流程/高吞吐交易",
            "解释器架构 (Interpreter Architecture)": "极致性能/规则很少/无需运行时配置",
            "规则系统架构 (Rule-Based System Architecture)": "规则很少/深度算法推理/高频低延迟核心交易",
            "进程通信架构 (Communicating Processes Architecture)": "极小单体工具/无需隔离/强共享内存",
            "多Agent架构 (Multi-Agent Architecture)": "确定性简单流程/极低延迟交易/缺少评估监控",
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
    # 注入 Neo4j 图上下文（关键词匹配 + 互补关系）
    kb = get_neo4j_kb()
    if kb.is_available():
        neo4j_context = kb.query_architecture_context(features.get("features", []))
        if neo4j_context:
            prompt += "\n\n" + neo4j_context
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
        # 课程经典风格触发词
        (["批处理"], ["批处理", "batch", "离线", "日终", "清算", "对账", "监管报表", "批量作业", "可重跑", "检查点"], 0.35),
        (["主程序-子过程"], ["主程序", "子过程", "main subroutine", "命令行工具", "固定流程", "本地工具", "过程式", "简单稳定"], 0.30),
        (["面向对象"], ["面向对象", "object oriented", "OO", "图形对象", "连接线", "属性面板", "撤销重做", "领域对象", "类", "对象"], 0.30),
        (["仓库"], ["仓库", "repository", "共享数据", "统一知识库", "中央数据", "多工具", "元数据", "知识管理"], 0.32),
        (["黑板"], ["黑板", "blackboard", "共享工作区", "知识源", "多模型", "增量推理", "协同诊断", "医生反馈"], 0.35),
        (["解释器"], ["解释器", "interpreter", "DSL", "脚本", "运行时解析", "脚本引擎", "模板", "字节码"], 0.35),
        (["规则系统"], ["规则系统", "rule based", "规则引擎", "推理机", "事实库", "规则库", "审批", "风控", "征信", "负债率", "可配置规则"], 0.35),
        (["进程通信"], ["进程通信", "communicating processes", "IPC", "多进程", "Socket", "RPC", "消息通道", "调度进程", "工作进程", "分布式爬虫"], 0.32),
        (["多Agent"], ["多Agent", "multi-agent", "智能体", "规划Agent", "检索Agent", "评审Agent", "协调Agent", "共享记忆", "任务分解"], 0.35),
    ]
    
    # 构建候选名称到架构的映射
    candidate_map = {}
    for c in candidates:
        name = c.get("name", "")
        for kb_name in full_kb:
            if kb_name in name or name in kb_name:
                candidate_map[kb_name] = c
                break

    def has_any(keywords: list[str]) -> bool:
        return any(keyword.lower() in req_lower for keyword in keywords)

    def find_candidate(keyword: str) -> dict | None:
        for candidate in candidates:
            if keyword.lower() in candidate.get("name", "").lower():
                return candidate
        return None

    def find_kb_name(keyword: str) -> str | None:
        for kb_name in full_kb:
            if keyword.lower() in kb_name.lower():
                return kb_name
        return None

    def ensure_candidate(keyword: str, score: float, reasons: list[str], risks: list[str] | None = None) -> None:
        if find_candidate(keyword):
            return
        kb_name = find_kb_name(keyword)
        if not kb_name:
            return
        candidates.append({
            "name": kb_name,
            "match_score": score,
            "match_reasons": reasons,
            "risks": risks or ["该风格由规则引擎根据强关键词补入，仍需结合具体非功能约束校验。"],
            "rule_engine_note": "强关键词触发：规则引擎补入候选",
        })
        for name in full_kb:
            if name == kb_name:
                candidate_map[name] = candidates[-1]
                break

    # Course-reference scenario:
    # cross-platform IM + massive online users + realtime reliable messages + future video calls
    # should rank Event-Driven as the core option and Microservices as the backup option.
    im_realtime_signal = has_any(["即时通讯", "im", "聊天", "消息", "实时", "万人", "在线", "视频通话", "跨平台"])
    cqrs_strong_signal = has_any(["银行", "交易", "转账", "存款", "贷款", "审计", "强一致", "事务", "读写分离", "事件溯源"])
    if im_realtime_signal and not cqrs_strong_signal:
        event_candidate = find_candidate("Event-Driven") or find_candidate("事件")
        if event_candidate:
            event_candidate["match_score"] = max(event_candidate.get("match_score", 0.0), 0.92)
            event_candidate["rule_engine_note"] = "即时通讯实时消息场景触发：事件驱动作为核心推荐"

        micro_candidate = find_candidate("Microservices") or find_candidate("微服务")
        if micro_candidate:
            micro_candidate["match_score"] = max(micro_candidate.get("match_score", 0.0), 0.90)
            micro_candidate.setdefault("match_reasons", []).append("视频通话等后续能力可拆分为独立服务，便于快速扩展")
            micro_candidate["rule_engine_note"] = "即时通讯扩展场景触发：微服务作为备选架构"
        else:
            micro_name = find_kb_name("Microservices") or find_kb_name("微服务")
            if micro_name:
                candidates.append({
                    "name": micro_name,
                    "match_score": 0.90,
                    "match_reasons": [
                        "视频通话等后续能力可拆分为独立服务，便于快速扩展",
                        "用户、消息、音视频、通知等模块可独立部署和水平扩容",
                    ],
                    "risks": [
                        "服务拆分会增加部署、监控和服务治理复杂度",
                        "跨服务调用需要处理链路追踪、限流和降级",
                    ],
                    "rule_engine_note": "即时通讯扩展场景触发：微服务作为备选架构",
                })

        cqrs_candidate = find_candidate("CQRS")
        if cqrs_candidate:
            cqrs_candidate["match_score"] = min(cqrs_candidate.get("match_score", 0.0), 0.58)
            cqrs_candidate["rule_engine_note"] = "该需求没有强交易/审计/读写分离信号，CQRS不作为主要候选"

        p2p_explicit_signal = has_any(["P2P", "对等", "点对点", "去中心化", "区块链", "CDN", "边缘节点", "文件共享"])
        if not p2p_explicit_signal:
            p2p_candidate = find_candidate("Peer-to-Peer") or find_candidate("对等") or find_candidate("P2P")
            if p2p_candidate:
                p2p_candidate["match_score"] = min(p2p_candidate.get("match_score", 0.0), 0.55)
                p2p_candidate["rule_engine_note"] = "即时通讯需求没有明确P2P/去中心化信号，对等架构不作为主要候选"
    
    # 应用正向加分
    for kb_names, keywords, boost in promotion_rules:
        if any(kw.lower() in req_lower for kw in keywords):
            for kb_name in kb_names:
                ensure_candidate(
                    kb_name,
                    min(0.96, 0.68 + boost),
                    [
                        f"需求中出现 {kb_name} 的强触发词：{', '.join([kw for kw in keywords if kw.lower() in req_lower][:3])}",
                        "该风格与课程经典体系结构分类中的适用场景一致。",
                    ],
                )
                for cand_name, cand in candidate_map.items():
                    if kb_name in cand_name:
                        old_score = cand.get("match_score", 0.5)
                        cand["match_score"] = min(1.0, old_score + boost)
                        cand["rule_engine_note"] = f"关键词触发加分 +{boost:.0%}"
                        logger.info(f"   规则引擎加分: {cand_name} +{boost:.0%} (关键词匹配)")
                        break

    batch_signal = has_any(["批处理", "batch", "离线", "日终", "清算", "对账", "监管报表", "批量作业", "可重跑"])
    if batch_signal:
        batch_candidate = find_candidate("批处理") or find_candidate("Batch")
        if batch_candidate:
            batch_candidate["match_score"] = max(batch_candidate.get("match_score", 0.0), 0.98)
            batch_candidate["rule_engine_note"] = "离线批量作业场景触发：批处理作为首选架构"
        cqrs_candidate = find_candidate("CQRS")
        if cqrs_candidate and not has_any(["转账", "支付", "存款", "贷款", "实时交易", "强一致事务"]):
            cqrs_candidate["match_score"] = min(cqrs_candidate.get("match_score", 0.0), 0.82)
            cqrs_candidate["rule_engine_note"] = "该需求更偏离线批量作业，CQRS作为审计/查询补充候选"
    
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

# ── Requirement-aware Topology ─────────────────────
def _topology_key(arch_name: str) -> str:
    name = arch_name.lower()
    if "cqrs" in name:
        return "cqrs"
    if "pipe" in name or "管道" in arch_name or "过滤器" in arch_name:
        return "pipe"
    if "规则系统" in arch_name or "rule" in name:
        return "rule_system"
    if "解释器" in arch_name or "interpreter" in name:
        return "interpreter"
    if "多agent" in name or "multi-agent" in name:
        return "multi_agent"
    if "黑板" in arch_name or "blackboard" in name:
        return "blackboard"
    if "仓库" in arch_name or "repository" in name:
        return "repository"
    if "批处理" in arch_name or "batch" in name:
        return "batch"
    if "进程通信" in arch_name or "communicating" in name:
        return "processes"
    if "面向对象" in arch_name or "object-oriented" in name or "object oriented" in name:
        return "object_oriented"
    if "主程序" in arch_name or "subroutine" in name:
        return "main_subroutine"
    if "microservice" in name or "微服务" in arch_name:
        return "microservices"
    if "event" in name or "事件" in arch_name:
        return "event"
    if "六边形" in arch_name or "hexagonal" in name:
        return "hexagonal"
    if "layered" in name or "分层" in arch_name:
        return "layered"
    return "default"

def _node(node_id: str, label: str, node_type: str, hint: str, x: int, y: int) -> dict:
    return {"id": node_id, "label": label, "type": node_type, "hint": hint, "x": x, "y": y}

def _edge(source: str, target: str, label: str, edge_type: str = "sync") -> dict:
    return {"from": source, "to": target, "label": label, "type": edge_type}

def build_requirement_topology(requirement: str, features: dict, candidates: list[dict]) -> dict:
    """基于需求特征和首选架构生成可视化拓扑模型，前端可直接渲染节点/边。"""
    top_name = candidates[0].get("name", "通用架构") if candidates else "通用架构"
    key = _topology_key(top_name)
    req = requirement.lower()
    domain = features.get("domain") or "目标系统"
    requirements = [
        *[str(x) for x in features.get("features", [])[:4]],
        *[str(x) for x in features.get("key_requirements", [])[:4]],
    ][:6]

    def pipe_labels() -> list[str]:
        if any(word in req for word in ["视频", "转码", "水印", "缩略图", "审核"]):
            return ["视频上传", "转码", "加水印", "生成缩略图", "内容审核", "发布/存储"]
        if any(word in req for word in ["ci/cd", "构建", "测试", "部署"]):
            return ["代码提交", "构建", "自动化测试", "制品归档", "审批", "部署"]
        return ["输入数据", "清洗", "转换", "校验", "聚合", "输出结果"]

    if key == "cqrs":
        transaction_label = "交易命令" if any(w in req for w in ["银行", "转账", "存款", "贷款"]) else "业务命令"
        read_label = "账户/审计查询" if "银行" in req else "查询模型"
        nodes = [
            _node("client", "用户/外部系统", "actor", f"来自需求领域：{domain}", 70, 230),
            _node("command", transaction_label, "command", "处理写操作和事务边界", 270, 155),
            _node("write_db", "写库/事件日志", "store", "保存权威事实和审计记录", 270, 330),
            _node("projection", "事件投影", "event", "把写侧事实同步到读模型", 500, 330),
            _node("query", read_label, "query", "面向高频读取优化", 700, 155),
            _node("read_db", "读库/缓存", "store", "支撑报表、历史和聚合查询", 700, 330),
        ]
        edges = [_edge("client", "command", "提交命令", "command"), _edge("command", "write_db", "事务写入", "command"), _edge("write_db", "projection", "发布领域事件", "event"), _edge("projection", "read_db", "更新投影视图", "event"), _edge("client", "query", "读取", "sync"), _edge("query", "read_db", "查询优化视图", "sync")]
    elif key == "pipe":
        labels = pipe_labels()
        nodes = [_node(f"step{i}", label, "filter" if i not in (0, len(labels) - 1) else "endpoint", f"需求定制步骤：{label}", 90 + i * 150, 245) for i, label in enumerate(labels)]
        edges = [_edge(f"step{i}", f"step{i+1}", "流转", "stream") for i in range(len(labels) - 1)]
    elif key == "rule_system":
        nodes = [
            _node("facts", "申请事实/输入数据", "store", "收入、征信、负债率等事实", 80, 255),
            _node("rules", "规则库", "store", "地区政策、风控和审批规则", 300, 130),
            _node("engine", "推理机", "compute", "匹配规则并解释决策", 490, 255),
            _node("audit", "命中记录", "store", "记录规则命中和人工复核依据", 680, 130),
            _node("decision", "审批结果", "output", "通过、拒绝或人工复核", 790, 255),
        ]
        edges = [_edge("facts", "engine", "输入事实"), _edge("rules", "engine", "加载规则"), _edge("engine", "audit", "记录解释", "event"), _edge("engine", "decision", "输出决策")]
    elif key == "multi_agent":
        nodes = [
            _node("user", "用户目标", "actor", f"任务领域：{domain}", 70, 250),
            _node("coordinator", "协调Agent", "agent", "拆解任务并汇总结论", 260, 250),
            _node("planner", "规划Agent", "agent", "制定步骤和约束", 470, 120),
            _node("researcher", "检索Agent", "agent", "收集资料和证据", 470, 250),
            _node("reviewer", "评审Agent", "agent", "校验结论和风险", 470, 380),
            _node("memory", "共享记忆/黑板", "store", "保存上下文、案例和中间结果", 720, 250),
        ]
        edges = [_edge("user", "coordinator", "提交目标"), _edge("coordinator", "planner", "分派规划", "message"), _edge("coordinator", "researcher", "分派检索", "message"), _edge("coordinator", "reviewer", "分派评审", "message"), _edge("planner", "memory", "写入计划", "event"), _edge("researcher", "memory", "写入证据", "event"), _edge("reviewer", "memory", "写入反馈", "event"), _edge("memory", "coordinator", "汇总上下文", "message")]
    elif key == "blackboard":
        nodes = [
            _node("source1", "影像/数据模型", "compute", "独立知识源", 90, 150),
            _node("source2", "文本/规则模型", "compute", "独立知识源", 90, 340),
            _node("controller", "控制器", "compute", "选择下一步推理", 370, 250),
            _node("blackboard", "共享黑板", "store", "沉淀中间结论和置信度", 600, 250),
            _node("result", "综合结论", "output", "面向用户输出", 810, 250),
        ]
        edges = [_edge("source1", "blackboard", "写入线索", "event"), _edge("source2", "blackboard", "写入线索", "event"), _edge("blackboard", "controller", "读取状态"), _edge("controller", "source1", "调度"), _edge("controller", "source2", "调度"), _edge("blackboard", "result", "形成结论")]
    elif key == "repository":
        nodes = [
            _node("tool1", "检索工具", "compute", "读取共享知识", 110, 130),
            _node("tool2", "标注/审核工具", "compute", "写入元数据", 110, 370),
            _node("repo", "中心知识库/仓库", "store", "统一文档、元数据和权限", 430, 250),
            _node("qa", "问答服务", "compute", "基于仓库生成回答", 720, 130),
            _node("governance", "权限/治理", "guard", "集中控制访问和版本", 720, 370),
        ]
        edges = [_edge("tool1", "repo", "查询/索引"), _edge("tool2", "repo", "写入标注"), _edge("repo", "qa", "检索上下文"), _edge("governance", "repo", "治理策略")]
    elif key == "batch":
        nodes = [
            _node("sources", "交易/业务数据源", "store", "批量输入", 80, 250),
            _node("scheduler", "作业调度器", "compute", "夜间、日终或定时触发", 270, 250),
            _node("batch", "批处理作业", "compute", "清算、对账、报表生成", 470, 250),
            _node("checkpoint", "检查点/审计日志", "store", "支持失败恢复和重跑", 670, 140),
            _node("output", "报表/结果库", "output", "监管报表或批量结果", 790, 300),
        ]
        edges = [_edge("sources", "scheduler", "提交批次"), _edge("scheduler", "batch", "触发作业"), _edge("batch", "checkpoint", "记录进度", "event"), _edge("batch", "output", "输出结果")]
    elif key == "processes":
        nodes = [
            _node("scheduler", "调度进程", "compute", "分配任务和URL", 130, 250),
            _node("queue", "消息通道", "event", "进程间通信", 330, 250),
            _node("worker1", "工作进程 A", "compute", "并发执行任务", 560, 140),
            _node("worker2", "工作进程 B", "compute", "并发执行任务", 560, 360),
            _node("result", "结果汇聚", "store", "回传抓取或计算结果", 800, 250),
        ]
        edges = [_edge("scheduler", "queue", "投递任务", "message"), _edge("queue", "worker1", "消费任务", "message"), _edge("queue", "worker2", "消费任务", "message"), _edge("worker1", "result", "回传结果", "message"), _edge("worker2", "result", "回传结果", "message")]
    else:
        nodes = [
            _node("entry", "用户入口", "actor", f"需求领域：{domain}", 90, 250),
            _node("core", top_name.split(" (")[0], "compute", "首选架构核心组件", 360, 250),
            _node("data", "数据/状态", "store", "承载业务数据和历史记录", 650, 150),
            _node("integration", "外部集成", "compute", "对接下游系统或服务", 650, 350),
        ]
        edges = [_edge("entry", "core", "请求/命令"), _edge("core", "data", "读写"), _edge("core", "integration", "调用/事件")]

    return {
        "title": f"{domain}的{top_name.split(' (')[0]}拓扑",
        "style_key": key,
        "arch_name": top_name,
        "requirements": list(dict.fromkeys(requirements)),
        "nodes": nodes,
        "edges": edges,
    }

# ── Step 4: Evaluation Agent ───────────────────────
EVALUATION_PROMPT = """你是一个软件架构评估专家。基于候选架构风格进行多维度对比分析。

候选架构及匹配分数：
{candidates}

用户需求：
{requirement}

Report date:
{report_date}

请生成一份专业评估报告，需包含以下部分（用中文）：
If the report includes a report date or evaluation date, use the exact Report date above. Do not invent or reuse example dates.

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
    
    today = date.today()
    messages = [
        SystemMessage(content=EVALUATION_PROMPT.format(
            candidates=json.dumps(validated, ensure_ascii=False, indent=2),
            requirement=state["user_requirement"],
            report_date=today.isoformat(),
        )),
        HumanMessage(content="请生成架构评估与推荐报告。"),
    ]
    response = await llm.ainvoke(messages)
    
    state["evaluation_report"] = response.content
    state["topology"] = build_requirement_topology(
        state["user_requirement"],
        state["extracted_features"],
        state["candidate_styles"],
    )
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
