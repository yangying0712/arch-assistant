"""
Neo4j 知识图谱查询模块
为 Agent Runtime 提供图数据库查询能力

使用方式:
    from .neo4j_kb import Neo4jKnowledgeBase
    kb = Neo4jKnowledgeBase()
    context = kb.query_architecture_context(features=[...])
"""
import os
from typing import Optional
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError
from loguru import logger


class Neo4jKnowledgeBase:
    """Neo4j 架构知识图谱查询封装"""

    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.auth = (os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "password123"))
        self._driver = None
        self._available = None  # 延迟检测

    @property
    def driver(self):
        if self._driver is None:
            self._driver = GraphDatabase.driver(self.uri, auth=self.auth)
        return self._driver

    def is_available(self) -> bool:
        """检测 Neo4j 是否可用"""
        if self._available is not None:
            return self._available
        try:
            with self.driver.session() as session:
                session.run("RETURN 1")
            self._available = True
            logger.info("✅ Neo4j 知识图谱连接成功")
        except (ServiceUnavailable, AuthError, OSError) as e:
            self._available = False
            logger.warning(f"⚠️ Neo4j 不可用，回退到 JSON 知识库: {e}")
        return self._available

    def get_all_styles_summary(self) -> list[dict]:
        """获取所有架构风格的摘要信息（含优缺点的扁平列表）"""
        if not self.is_available():
            return []
        with self.driver.session() as session:
            result = session.run("""
                MATCH (a:ArchitectureStyle)
                OPTIONAL MATCH (a)-[:HAS_PRO]->(p:Characteristic)
                OPTIONAL MATCH (a)-[:HAS_CON]->(c:Characteristic)
                OPTIONAL MATCH (a)-[:HAS_KEYWORD]->(k:Keyword)
                RETURN a.name AS name,
                       a.category AS category,
                       a.description AS desc,
                       a.keywords AS keywords,
                       a.anti_keywords AS anti_keywords,
                       collect(DISTINCT p.name) AS pros,
                       collect(DISTINCT c.name) AS cons,
                       collect(DISTINCT k.name) AS kw_list
                ORDER BY a.name
            """)
            return [dict(record) for record in result]

    def get_styles_by_keyword(self, keywords: list[str], limit: int = 5) -> list[dict]:
        """根据关键词匹配架构风格（用于规则引擎触发）"""
        if not self.is_available():
            return []
        with self.driver.session() as session:
            result = session.run("""
                MATCH (a:ArchitectureStyle)-[:HAS_KEYWORD]->(k:Keyword)
                WHERE k.name IN $keywords
                WITH a, count(k) AS matches
                ORDER BY matches DESC
                LIMIT $limit
                MATCH (a)-[:HAS_PRO]->(p:Characteristic)
                MATCH (a)-[:HAS_CON]->(c:Characteristic)
                RETURN a.name AS name,
                       a.category AS category,
                       a.description AS desc,
                       collect(DISTINCT p.name) AS pros,
                       collect(DISTINCT c.name) AS cons,
                       matches
            """, keywords=keywords, limit=limit)
            return [dict(record) for record in result]

    def get_style_detail(self, style_name: str) -> Optional[dict]:
        """获取单个架构风格的完整信息"""
        if not self.is_available():
            return None
        with self.driver.session() as session:
            result = session.run("""
                MATCH (a:ArchitectureStyle {name: $name})
                OPTIONAL MATCH (a)-[:HAS_PRO]->(p:Characteristic)
                OPTIONAL MATCH (a)-[:HAS_CON]->(c:Characteristic)
                OPTIONAL MATCH (a)-[:SUITABLE_FOR]->(u:UseCase)
                OPTIONAL MATCH (a)-[:COMPLEMENTS]->(comp:ArchitectureStyle)
                OPTIONAL MATCH (a)-[:RELATED_TO]->(rel:ArchitectureStyle)
                RETURN a.name AS name,
                       a.category AS category,
                       a.description AS desc,
                       a.keywords AS keywords,
                       a.anti_keywords AS anti_keywords,
                       collect(DISTINCT p.name) AS pros,
                       collect(DISTINCT c.name) AS cons,
                       collect(DISTINCT u.name) AS usecases,
                       collect(DISTINCT comp.name) AS complements,
                       collect(DISTINCT rel.name) AS related
            """, name=style_name)
            record = result.single()
            return dict(record) if record else None

    def get_complementary_styles(self, style_name: str) -> list[dict]:
        """获取某个架构风格的互补架构（通过 COMPLEMENTS 边）"""
        if not self.is_available():
            return []
        with self.driver.session() as session:
            result = session.run("""
                MATCH (a:ArchitectureStyle {name: $name})-[r:COMPLEMENTS]->(b:ArchitectureStyle)
                RETURN b.name AS name, b.description AS desc, r.reason AS reason
                UNION
                MATCH (b:ArchitectureStyle)-[r:COMPLEMENTS]->(a:ArchitectureStyle {name: $name})
                RETURN b.name AS name, b.description AS desc, r.reason AS reason
            """, name=style_name)
            return [dict(record) for record in result]

    def query_architecture_context(self, features: list[str]) -> str:
        """核心方法：根据提取的需求特征，生成图查询上下文文本

        用于注入到 LLM Prompt 中，替代原有的 JSON 知识摘要。
        返回：结构化的知识图谱上下文文本，可直接拼接到 System Prompt。
        """
        if not self.is_available():
            return ""

        lines = ["【Neo4j 知识图谱上下文】"]

        # 1. 关键词触发：看哪些架构匹配到当前特征
        matched = self.get_styles_by_keyword(features, limit=8)
        if matched:
            lines.append("\n📌 关键词匹配到的架构风格:")
            for m in matched:
                kw_match = m.get('matches', 0)
                lines.append(
                    f"  • {m['name']} [{m['category']}] "
                    f"(关键词命中: {kw_match}) | "
                    f"优点: {', '.join(m.get('pros', [])[:3])} | "
                    f"缺点: {', '.join(m.get('cons', [])[:2])}"
                )

        # 2. 全量架构摘要（含触发词和排除词）
        all_styles = self.get_all_styles_summary()
        if all_styles:
            lines.append("\n📋 完整架构知识库（含触发/排除规则）:")
            for s in all_styles:
                kws = ', '.join(s.get('keywords', [])[:4])
                antis = ', '.join(s.get('anti_keywords', [])[:3])
                lines.append(
                    f"  - {s['name']} [{s.get('category','')}] | "
                    f"触发词: {kws} | "
                    f"排除词: {antis} | "
                    f"优点: {', '.join(s.get('pros', [])[:2])}"
                )

        # 3. 互补关系
        lines.append("\n🔗 架构间互补关系:")
        complements_found = False
        for s in all_styles[:12]:
            comps = self.get_complementary_styles(s.get('name', ''))
            if comps:
                complements_found = True
                for c in comps:
                    lines.append(f"  {s['name']} ⟷ {c['name']}: {c.get('reason','优势互补')}")
        if not complements_found:
            lines.append("  (暂无)")

        return "\n".join(lines)

    def close(self):
        if self._driver:
            self._driver.close()
            self._driver = None
