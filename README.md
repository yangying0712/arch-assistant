# Architecture Assistant

基于大语言模型的软件架构风格智能助手。项目面向《软件体系结构》课程大作业，目标是从自然语言需求出发，自动完成需求特征提取、候选架构推荐、多维度决策分析、拓扑图展示和评估报告生成。

## 核心能力

- 自然语言需求理解：提取并发量、一致性、扩展性、部署约束、关键业务特征。
- 架构推荐：返回至少 3 种候选体系结构风格，并给出匹配度、推荐理由和风险提示。
- 决策支持：展示候选架构对比、质量属性雷达、架构拓扑图、决策溯源和组合推荐。
- LLM + 规则引擎混合推理：DeepSeek 负责语义理解与报告生成，规则引擎负责校验、加权和反偏见约束。
- 知识进化：自动保存历史分析案例，后续相似需求可作为 Few-shot 上下文参考。
- Web 演示：Vue 前端由 API Gateway 托管，支持流式输出、报告打字机效果、日夜主题切换和语音输入。

## 系统架构

```text
Browser / Vue UI
        |
        | HTTP / SSE
        v
API Gateway :3000
        |
        v
Orchestration Engine :8001
        |
        +------> Agent Runtime :8003
        |           |
        |           +-- RequirementAnalysisAgent
        |           +-- ArchitectureMatchingAgent
        |           +-- EvaluationAgent
        |
        +------> LLM Router :8002
                    |
                    +-- DeepSeek API
```

## 服务划分

| 服务 | 端口 | 职责 |
|---|---:|---|
| API Gateway | 3000 | 统一入口、Web 前端托管、API/SSE 转发 |
| Orchestration Engine | 8001 | 分析流水线编排、缓存、上游服务协调 |
| Agent Runtime | 8003 | LangGraph 三 Agent 协作、规则引擎、知识进化 |
| LLM Router | 8002 | 统一 LLM 调用入口，代理 DeepSeek 请求 |

## 目录结构

```text
apps/
  api-gateway/              # 统一入口与前端静态资源托管
  orchestration-engine/     # 流水线编排与缓存
  agent-runtime/            # 多 Agent 推理与知识库逻辑
  llm-router/               # LLM API 代理
frontend/                   # Vue 前端
data/
  architecture_styles.json  # 12 种架构风格知识库
  test_scenarios.json       # 20 个典型测试场景
  learned_cases.json        # 运行时学习案例
docs/
  需求规格说明书.md
  架构设计文档.md
  测试报告.md
  答辩材料.md
scripts/
  start-local-windows.ps1   # Windows 本地一键启动脚本
```

## 环境准备

1. 创建或确认 Python 虚拟环境。

```powershell
python -m venv .venv-win
.\.venv-win\Scripts\pip install -r requirements.txt
```

2. 安装前端依赖并构建。

```powershell
npm.cmd --prefix frontend install
npm.cmd --prefix frontend run build
```

3. 配置环境变量。

复制 `.env.example` 为 `.env`，填写 DeepSeek API Key。

```text
DEEPSEEK_API_KEY=your_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
```

## 启动方式

推荐使用 Windows 启动脚本：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\start-local-windows.ps1
```

脚本会启动：

- `http://127.0.0.1:8002` LLM Router
- `http://127.0.0.1:8003` Agent Runtime
- `http://127.0.0.1:8001` Orchestration Engine
- `http://127.0.0.1:3000` API Gateway + Vue 前端

打开浏览器访问：

```text
http://localhost:3000/
```

## 健康检查

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:3000/health
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8001/health
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8002/health
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8003/health
```

预期均返回 `status: healthy`。

## API 示例

普通分析：

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:3000/api/v1/analyze `
  -ContentType "application/json" `
  -Body '{"prompt":"开发银行核心交易系统，需要处理转账、存款、贷款等业务，对数据一致性和审计追踪有极高要求，支持日均百万笔交易。","session_id":"demo"}'
```

流式分析：

```powershell
curl.exe -N -X POST http://127.0.0.1:3000/api/v1/analyze/stream ^
  -H "Content-Type: application/json" ^
  -d "{\"prompt\":\"开发银行核心交易系统，需要处理转账、存款、贷款等业务，对数据一致性和审计追踪有极高要求，支持日均百万笔交易。\",\"session_id\":\"demo-stream\"}"
```

## 作业要求对应关系

| 作业要求 | 项目实现 |
|---|---|
| 微服务主体架构 | 4 个 FastAPI 微服务 |
| 至少 3 类智能体 | 需求解析、架构匹配、评估生成 |
| 集成 LLM | DeepSeek，经 LLM Router 调用 |
| ≥10 种架构风格知识库 | `architecture_styles.json` 覆盖 12 种 |
| ≥20 个测试场景 | `test_scenarios.json` 覆盖 20 个 |
| 返回 ≥3 种候选架构 | 候选卡片按匹配度排序 |
| 规则引擎 + LLM 混合推理 | `agent_runtime/graph.py` 中实现规则校验 |
| 可视化对比与拓扑图 | 前端雷达图、候选卡片、拓扑图、决策溯源 |
| Web API 接口 | `/api/v1/analyze` 与 `/api/v1/analyze/stream` |
| 开发文档 | `docs/需求规格说明书.md`、`docs/架构设计文档.md`、`docs/测试报告.md` |
| 答辩材料 | `docs/答辩材料.md` |

## 演示建议

推荐演示输入：

```text
开发银行核心交易系统，需要处理转账、存款、贷款等业务，对数据一致性和审计追踪有极高要求，支持日均百万笔交易。
```

预期展示链路：

1. 需求特征先流式出现。
2. 候选架构出现，首选通常为 CQRS。
3. 展示质量属性雷达与 CQRS 拓扑图。
4. 展示决策溯源与组合推荐。
5. 评估报告以打字机效果逐步呈现。

## 已知说明

- Neo4j 为可选增强项。当前系统优先尝试 Neo4j，连接不可用时自动回退到 JSON 知识库。
- 语音输入依赖浏览器 Web Speech API，推荐使用 Chrome 或 Edge，并通过 `localhost` 访问。
- `data/learned_cases.json` 是运行时学习数据，会随演示增长，通常不作为代码变更提交。
