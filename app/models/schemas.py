# app/models/schemas.py
"""请求和响应的 Pydantic 模型"""
#BaseModel  →  定义"模型的骨架"（有哪些字段、什么类型）
#Field      →  定义"每个字段的细节"（必填、长度、范围、描述）
#ConfigDict →  定义"整个模型的行为"（序列化方式、ORM 兼容等）
#`BaseModel` 建模型、`Field` 管单字段约束、`ConfigDict` 管全局行为——三者配合，
# 就能定义出带完整校验、序列化能力的请求/响应数据结构。
from pydantic import BaseModel, Field, ConfigDict
# `Literal` 用于把字段的取值范围"锁定"为几个指定值，让 Pydantic 
# 在校验时自动拦截超出范围的输入——是定义固定选项字段（如聊天角色）最简洁的方式。
from typing import Literal
from datetime import datetime

# ===== 聊天相关 =====
 
class ChatMessage(BaseModel):
    """一条聊天消息"""
    role: Literal["system", "user", "assistant"] = Field(
        ..., description="消息角色"
    )
    content: str = Field(..., min_length=1, description="消息内容")

class ChatRequest(BaseModel):
    """POST /chat 的请求体"""
    model_config = ConfigDict(
        extra="forbid",  # 拒绝额外的未知字段
        json_schema_extra={
            "example": {
                "model": "deepseek",
                "messages": [
                    {"role": "system", "content": "你是 Python 编程助手"},
                    {"role": "user", "content": "写一个冒泡排序"},
                ],
                "temperature": 0.7,
                "max_tokens": 4096,
                "stream": False,
            }
        }
    )

    model: str = Field(
        default="deepseek",
        description="模型 ID: 'deepseek' 或 'openai'"
    )
    messages: list[ChatMessage] = Field(
        ..., min_length=1, max_length=50,
        description="对话消息列表，至少 1 条，最多 50 条"
    )
    temperature: float = Field(
        default=0.7, ge=0.0, le=2.0,
        description="随机性: 0= 最保守, 1= 平衡, 2= 最冒险"
    )
    max_tokens: int = Field(
        default=4096, ge=1, le=16384,
        description="最大返回 Token 数"
    )
    stream: bool = Field(
        default=False,
        description="是否使用流式输出（SSE）"
    )

class ChatResponse(BaseModel):
    """POST /chat 的响应体"""
    id: str = Field(..., description="响应 ID")
    model: str = Field(..., description="使用的模型")
    content: str = Field(..., description="助手的回复内容")
    usage: dict = Field(
        default_factory=dict,
        description="Token 使用情况: {prompt_tokens, completion_tokens, total_tokens}"
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="响应时间"
    )

class ChatError(BaseModel):
    """错误响应体"""
    error: str = Field(..., description="错误类型")
    message: str = Field(..., description="错误详情")
    model: str | None = Field(default=None, description="出错的模型")
 
 # ===== 模型列表相关 =====
 
class ModelInfo(BaseModel):
    """单个模型的信息"""
    id: str
    name: str
    provider: str
    description: str

class ModelListResponse(BaseModel):
    """GET /models 的响应体"""
    models: list[ModelInfo]
    default: str = Field(description="默认使用的模型 ID")
    total: int = Field(description="可用模型总数")
 
 # ===== 健康检查相关 =====
 
class HealthResponse(BaseModel):
    """GET /health 的响应体"""
    status: Literal["healthy", "degraded"]
    version: str
    environment: str
    models_available: int
    uptime_seconds: int


 