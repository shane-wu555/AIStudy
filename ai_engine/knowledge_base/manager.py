"""
知识库管理
存储和检索教育资源与知识
"""
from typing import List, Dict, Optional
from datetime import datetime
import json


class KnowledgeItem:
    """知识条目"""
    
    def __init__(
        self,
        title: str,
        content: str,
        subject: str,
        topics: List[str],
        difficulty: str = "medium",
        **metadata
    ):
        self.id = f"kb_{datetime.now().timestamp()}"
        self.title = title
        self.content = content
        self.subject = subject  # math, physics, chemistry, etc.
        self.topics = topics
        self.difficulty = difficulty  # easy, medium, hard
        self.metadata = metadata
        self.created_at = datetime.now()
        self.embedding: Optional[List[float]] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "subject": self.subject,
            "topics": self.topics,
            "difficulty": self.difficulty,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }


class KnowledgeBase:
    """知识库"""
    
    def __init__(self):
        # 内存存储（生产环境应使用向量数据库如Milvus, Qdrant）
        self.items: Dict[str, KnowledgeItem] = {}
        self.index_by_subject: Dict[str, List[str]] = {}
        self.index_by_topic: Dict[str, List[str]] = {}
    
    def add_item(self, item: KnowledgeItem):
        """添加知识条目"""
        self.items[item.id] = item
        
        # 建立索引
        if item.subject not in self.index_by_subject:
            self.index_by_subject[item.subject] = []
        self.index_by_subject[item.subject].append(item.id)
        
        for topic in item.topics:
            if topic not in self.index_by_topic:
                self.index_by_topic[topic] = []
            self.index_by_topic[topic].append(item.id)
    
    def search_by_topic(
        self,
        topics: List[str],
        subject: Optional[str] = None,
        limit: int = 10
    ) -> List[KnowledgeItem]:
        """按知识点搜索"""
        result_ids = set()
        
        for topic in topics:
            if topic in self.index_by_topic:
                result_ids.update(self.index_by_topic[topic])
        
        results = [self.items[id] for id in result_ids if id in self.items]
        
        # 按学科过滤
        if subject:
            results = [r for r in results if r.subject == subject]
        
        # 按相关度排序（简化版）
        results.sort(
            key=lambda x: len(set(x.topics) & set(topics)),
            reverse=True
        )
        
        return results[:limit]
    
    def get_item(self, item_id: str) -> Optional[KnowledgeItem]:
        """获取知识条目"""
        return self.items.get(item_id)


class VectorRetriever:
    """向量检索器"""
    
    def __init__(self, knowledge_base: KnowledgeBase):
        self.knowledge_base = knowledge_base
    
    async def semantic_search(
        self,
        query: str,
        top_k: int = 5,
        subject: Optional[str] = None
    ) -> List[Dict]:
        """
        语义搜索
        TODO: 使用向量数据库进行相似度搜索
        """
        # 1. 将query转换为向量
        # from backend_service.model_interface.model_service import model_service
        # query_embedding = await model_service.get_embedding(query)
        
        # 2. 在向量数据库中搜索相似条目
        # results = vector_db.search(query_embedding, top_k)
        
        # 简化版: 返回固定示例
        sample_results = [
            {
                "id": "kb_001",
                "title": "一元二次方程求解方法",
                "content": "一元二次方程的标准形式为 ax² + bx + c = 0...",
                "relevance_score": 0.92
            }
        ]
        
        return sample_results
    
    async def hybrid_search(
        self,
        query: str,
        topics: List[str],
        top_k: int = 5
    ) -> List[Dict]:
        """
        混合搜索（关键词 + 语义）
        """
        # 1. 语义搜索
        semantic_results = await self.semantic_search(query, top_k)
        
        # 2. 关键词搜索
        keyword_results = self.knowledge_base.search_by_topic(topics, limit=top_k)
        
        # 3. 合并去重
        combined = {}
        for r in semantic_results:
            combined[r["id"]] = r
        
        for item in keyword_results:
            if item.id not in combined:
                combined[item.id] = {
                    **item.to_dict(),
                    "relevance_score": 0.7
                }
        
        # 按相关度排序
        results = sorted(
            combined.values(),
            key=lambda x: x.get("relevance_score", 0),
            reverse=True
        )
        
        return results[:top_k]


class KnowledgeManager:
    """知识库管理器"""
    
    def __init__(self):
        self.kb = KnowledgeBase()
        self.retriever = VectorRetriever(self.kb)
        self._load_initial_data()
    
    def _load_initial_data(self):
        """加载初始知识数据"""
        # 示例：添加一些基础知识
        math_items = [
            KnowledgeItem(
                title="一元二次方程求根公式",
                content="对于方程 ax² + bx + c = 0，求根公式为 x = (-b ± √(b²-4ac)) / 2a",
                subject="math",
                topics=["代数", "一元二次方程", "求根公式"],
                difficulty="medium",
                formula="x = (-b ± √(b²-4ac)) / 2a"
            ),
            KnowledgeItem(
                title="因式分解法",
                content="当方程可以因式分解时，可以将其写成 (x-a)(x-b)=0 的形式",
                subject="math",
                topics=["代数", "因式分解", "一元二次方程"],
                difficulty="easy"
            ),
        ]
        
        for item in math_items:
            self.kb.add_item(item)
    
    async def search(
        self,
        query: str,
        topics: List[str] = None,
        subject: Optional[str] = None,
        method: str = "hybrid"
    ) -> List[Dict]:
        """
        统一搜索接口
        """
        if method == "semantic":
            return await self.retriever.semantic_search(query, subject=subject)
        elif method == "keyword" and topics:
            results = self.kb.search_by_topic(topics, subject)
            return [r.to_dict() for r in results]
        else:  # hybrid
            return await self.retriever.hybrid_search(query, topics or [])


# 全局知识库实例
knowledge_manager = KnowledgeManager()
