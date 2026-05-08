# 🏗️ 软件架构风格智能助手

基于大语言模型（DeepSeek）和 LangGraph 多 Agent 协作的软件架构风格推荐系统。

> 《软件体系结构》课程大作业

## 系统架构

```
用户 → API Gateway (:3000) → Orchestration Engine (:8001) → Agent Runtime (:8003) + LLM Router (:8002)
```

### 微服务拆分

| 服务 | 端口 | 职责 |
|------|------|------|
| api-gateway | 3000 | 统一入口，Web UI + REST API |
| orchestration-engine | 8001 | 流水线编排，缓存管理 |
| agent-runtime | 8003 | 三 Agent 协作（需求解析→架构匹配→评估生成） |
| llm-router | 8002 | LLM 推理（DeepSeek） |

### 三 Agent 协作流程

```
用户需求 → RequirementAnalysisAgent（特征提取）
         → ArchitectureMatchingAgent（知识库匹配 + 规则引擎校验）
         → EvaluationAgent（多维度对比 + 推荐报告）
```

## 快速开始

```bash
# 1. 配置 API Key
cp .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY

# 2. 启动所有服务
docker-compose up -d

# 3. 打开浏览器
open http://localhost:3000
```

### 本地开发

```bash
pip install -r requirements.txt

# 启动各个服务（不同终端）
uvicorn apps.llm-router.llm_router.main:app --port 8002 --reload
uvicorn apps.agent-runtime.agent_runtime.main:app --port 8003 --reload
uvicorn apps.orchestration-engine.orchestration_engine.main:app --port 8001 --reload
uvicorn apps.api-gateway.api_gateway.main:app --port 3000 --reload
```

## API

```bash
# 分析需求
curl -X POST http://localhost:3000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "开发一个跨平台的即时通讯系统，要求支持万人同时在线，需要保证消息的实时性和可靠性"}'

# 流式分析
curl -X POST http://localhost:3000/api/v1/analyze/stream \
  -H "Content-Type: application/json" \
  -d '{"prompt": "构建一个大型B2C电商平台..."}'
```

## 知识库

`data/architecture_styles.json` 包含 12 种架构风格：
分层、微服务、事件驱动、CQRS、管道-过滤器、SOA、六边形、MVC、Space-Based、P2P、Serverless、插件架构

## 测试数据集

`data/test_scenarios.json` 包含 20 个典型需求场景案例。

## 技术栈

- **Agent 框架**: LangGraph + LangChain
- **LLM**: DeepSeek Chat
- **后端**: FastAPI + Uvicorn
- **容器化**: Docker Compose
- **知识库**: JSON 结构化数据（可扩展为 Neo4j）
