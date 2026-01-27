"""
AI模型调用抽象层
提供统一接口接入各厂商LLM/VLM
支持: OpenAI, Anthropic, 国产大模型(文心、通义、智谱等)
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from enum import Enum


class ModelProvider(Enum):
    """模型提供商"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    WENXIN = "wenxin"  # 百度文心一言
    TONGYI = "tongyi"  # 阿里通义千问
    ZHIPU = "zhipu"    # 智谱AI
    CUSTOM = "custom"


class ModelInterface(ABC):
    """模型接口抽象基类"""
    
    def __init__(self, api_key: str, **config):
        self.api_key = api_key
        self.config = config
    
    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Dict:
        """
        聊天接口
        Args:
            messages: 消息列表 [{"role": "user/assistant", "content": "..."}]
        Returns:
            {"content": "回复内容", "usage": {...}}
        """
        pass
    
    @abstractmethod
    async def vision(
        self,
        image_url: str,
        prompt: str,
        **kwargs
    ) -> Dict:
        """
        视觉理解接口 (VLM)
        Args:
            image_url: 图片URL或base64
            prompt: 提示词
        Returns:
            {"content": "识别结果", "confidence": 0.95}
        """
        pass
    
    @abstractmethod
    async def embedding(
        self,
        text: str,
        **kwargs
    ) -> List[float]:
        """
        文本嵌入接口
        Args:
            text: 待嵌入文本
        Returns:
            向量列表
        """
        pass


class OpenAIModel(ModelInterface):
    """OpenAI模型实现"""
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict:
        # TODO: 实现OpenAI API调用
        # import openai
        # response = await openai.ChatCompletion.acreate(
        #     model=self.config.get("model", "gpt-4"),
        #     messages=messages,
        #     **kwargs
        # )
        return {
            "content": "OpenAI模型回复（待实现）",
            "usage": {"total_tokens": 100}
        }
    
    async def vision(self, image_url: str, prompt: str, **kwargs) -> Dict:
        # TODO: 实现GPT-4V调用
        return {
            "content": "图像识别结果（待实现）",
            "confidence": 0.95
        }
    
    async def embedding(self, text: str, **kwargs) -> List[float]:
        # TODO: 实现embedding调用
        return [0.1] * 1536  # text-embedding-ada-002 维度


class WenxinModel(ModelInterface):
    """百度文心一言模型实现"""
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict:
        # TODO: 实现文心一言API调用
        return {
            "content": "文心一言模型回复（待实现）",
            "usage": {"total_tokens": 100}
        }
    
    async def vision(self, image_url: str, prompt: str, **kwargs) -> Dict:
        # TODO: 实现文心视觉理解
        return {
            "content": "图像识别结果（待实现）",
            "confidence": 0.95
        }
    
    async def embedding(self, text: str, **kwargs) -> List[float]:
        # TODO: 实现文心embedding
        return [0.1] * 768


class ModelFactory:
    """模型工厂"""
    
    _models = {
        ModelProvider.OPENAI: OpenAIModel,
        ModelProvider.WENXIN: WenxinModel,
        # TODO: 添加更多模型实现
    }
    
    @classmethod
    def create_model(
        cls,
        provider: ModelProvider,
        api_key: str,
        **config
    ) -> ModelInterface:
        """创建模型实例"""
        model_class = cls._models.get(provider)
        if not model_class:
            raise ValueError(f"不支持的模型提供商: {provider}")
        
        return model_class(api_key, **config)


class ModelService:
    """模型服务 - 统一调用入口"""
    
    def __init__(self):
        self.models: Dict[str, ModelInterface] = {}
        self.default_provider = ModelProvider.OPENAI
    
    def register_model(
        self,
        name: str,
        provider: ModelProvider,
        api_key: str,
        **config
    ):
        """注册模型"""
        model = ModelFactory.create_model(provider, api_key, **config)
        self.models[name] = model
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model_name: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """
        调用聊天模型
        """
        model = self._get_model(model_name)
        return await model.chat(messages, **kwargs)
    
    async def analyze_image(
        self,
        image_url: str,
        prompt: str = "请描述这张图片中的数学问题",
        model_name: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """
        分析图片（用于拍照题目识别）
        """
        model = self._get_model(model_name)
        return await model.vision(image_url, prompt, **kwargs)
    
    async def get_embedding(
        self,
        text: str,
        model_name: Optional[str] = None,
        **kwargs
    ) -> List[float]:
        """
        获取文本向量（用于知识检索）
        """
        model = self._get_model(model_name)
        return await model.embedding(text, **kwargs)
    
    def _get_model(self, model_name: Optional[str] = None) -> ModelInterface:
        """获取模型实例"""
        if model_name and model_name in self.models:
            return self.models[model_name]
        
        # 使用默认模型
        if not self.models:
            raise RuntimeError("未注册任何模型")
        
        return next(iter(self.models.values()))


# 全局服务实例
model_service = ModelService()

# 初始化示例
# model_service.register_model(
#     "gpt4",
#     ModelProvider.OPENAI,
#     api_key="your-api-key",
#     model="gpt-4-turbo-preview"
# )
