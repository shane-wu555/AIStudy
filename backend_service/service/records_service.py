"""
学习记录服务
管理学习历史、统计数据、进度追踪
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from enum import Enum


class RecordType(Enum):
    """记录类型"""
    QUESTION = "question"  # 提问
    PRACTICE = "practice"  # 练习
    REVIEW = "review"      # 复习
    ACHIEVEMENT = "achievement"  # 成就


class LearningRecord:
    """学习记录模型"""
    
    def __init__(
        self,
        user_id: str,
        title: str,
        description: str,
        record_type: RecordType,
        **metadata
    ):
        self.id = f"record_{datetime.now().timestamp()}"
        self.user_id = user_id
        self.title = title
        self.description = description
        self.type = record_type.value
        self.timestamp = datetime.now()
        self.metadata = metadata
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "type": self.type,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


class RecordsService:
    """学习记录服务"""
    
    def __init__(self):
        # 内存存储（生产环境应使用数据库）
        self.records: Dict[str, List[LearningRecord]] = {}
    
    def add_record(
        self,
        user_id: str,
        title: str,
        description: str,
        record_type: RecordType,
        **metadata
    ) -> LearningRecord:
        """添加学习记录"""
        record = LearningRecord(
            user_id=user_id,
            title=title,
            description=description,
            record_type=record_type,
            **metadata
        )
        
        if user_id not in self.records:
            self.records[user_id] = []
        
        self.records[user_id].append(record)
        return record
    
    def get_records(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        record_type: Optional[str] = None
    ) -> Dict:
        """
        获取学习记录
        UC06: 学习轨迹管理
        """
        user_records = self.records.get(user_id, [])
        
        # 按类型过滤
        if record_type:
            user_records = [r for r in user_records if r.type == record_type]
        
        # 按时间倒序排序
        user_records.sort(key=lambda x: x.timestamp, reverse=True)
        
        # 分页
        start = (page - 1) * page_size
        end = start + page_size
        page_records = user_records[start:end]
        
        return {
            "total": len(user_records),
            "page": page,
            "page_size": page_size,
            "records": [r.to_dict() for r in page_records]
        }
    
    def get_statistics(self, user_id: str) -> Dict:
        """
        获取学习统计数据
        """
        user_records = self.records.get(user_id, [])
        
        if not user_records:
            return {
                "study_days": 0,
                "total_hours": 0,
                "completed_problems": 0,
                "mastered_topics": 0
            }
        
        # 计算学习天数
        dates = set(r.timestamp.date() for r in user_records)
        study_days = len(dates)
        
        # 统计各类型记录数量
        type_counts = {}
        for record in user_records:
            type_counts[record.type] = type_counts.get(record.type, 0) + 1
        
        # TODO: 从metadata中提取更多统计信息
        total_hours = sum(
            r.metadata.get("duration_minutes", 0) 
            for r in user_records
        ) / 60
        
        return {
            "study_days": study_days,
            "total_hours": round(total_hours, 1),
            "completed_problems": type_counts.get("practice", 0),
            "mastered_topics": len(self._extract_topics(user_records)),
            "type_distribution": type_counts,
            "recent_activity": self._get_recent_activity(user_records)
        }
    
    def _extract_topics(self, records: List[LearningRecord]) -> set:
        """提取涉及的知识点"""
        topics = set()
        for record in records:
            if "topics" in record.metadata:
                topics.update(record.metadata["topics"])
        return topics
    
    def _get_recent_activity(
        self,
        records: List[LearningRecord],
        days: int = 7
    ) -> List[Dict]:
        """获取最近活动"""
        cutoff = datetime.now() - timedelta(days=days)
        recent = [r for r in records if r.timestamp >= cutoff]
        
        # 按日期分组
        daily_activity = {}
        for record in recent:
            date_key = record.timestamp.date().isoformat()
            if date_key not in daily_activity:
                daily_activity[date_key] = {
                    "date": date_key,
                    "count": 0,
                    "types": {}
                }
            
            daily_activity[date_key]["count"] += 1
            record_type = record.type
            daily_activity[date_key]["types"][record_type] = \
                daily_activity[date_key]["types"].get(record_type, 0) + 1
        
        return sorted(
            daily_activity.values(),
            key=lambda x: x["date"],
            reverse=True
        )


# 全局服务实例
records_service = RecordsService()
