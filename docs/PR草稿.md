# PR 草稿：架构知识库扩展与需求定制拓扑

## Summary

- 将架构风格知识库从 12 种扩展到 21 种，补齐课程经典五大类中的批处理、主程序-子过程、面向对象、仓库、黑板、解释器、规则系统、进程通信、多 Agent 等风格。
- 新增需求定制拓扑输出，后端根据用户需求、首选架构和候选结果生成 `topology.nodes/edges`，前端优先渲染动态拓扑。
- 增强知识进化链路：相似历史案例作为 Few-shot 参考，同时透传到前端决策溯源；测试 session 不写入案例库。
- 测试场景从 20 个扩展到 29 个，覆盖新增经典架构风格。
- 同步更新 README 与 docs 文档，补充验收分工、29 场景测试基准、Neo4j/RAG、CodeGraph 和动态拓扑说明。

## Verification

- JSON parse: `architecture_styles.json`、`test_scenarios.json`、`learned_cases.json`
- Python import: `agent_runtime.main`、`orchestration_engine.main`、`api_gateway.main`
- Frontend build: `npm.cmd --prefix frontend run build`
- Rule smoke:
  - 银行日终清算 -> 批处理架构
  - 信贷审批规则引擎 -> 规则系统架构
  - 多Agent研究助手 -> 多Agent架构
  - 视频转码/水印/审核 -> 管道-过滤器拓扑
- Docs review: README、需求规格说明书、架构设计文档、测试报告、答辩材料、验收小组分工文档已对齐当前实现。

## Residual Risk

- 完整 LLM 端到端效果依赖 `DEEPSEEK_API_KEY` 和外部模型响应稳定性。
- 批量测试数据集已扩展到 29 个场景，验收前应重新运行 `run_tests.py` 并刷新最新测试结果。
