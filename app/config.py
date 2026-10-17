# app/config.py
"""应用配置——所有环境相关的变量都在这里"""
from pydantic_settings import BaseSettings
#`lru_cache` 是装饰器，用来 缓存`Settings()` 实例 ，确保整个应用只读取一次环境变量，后续调用`get_settings()` 直接返回同一个对象，避免重复 IO。
#它让配置实例变成"只创建一次、全应用共享"的单例，避免重复读取环境变量的开销。
from functools import lru_cache

#`class Settings(BaseSettings)` 声明了一个 专注于应用配置的类 ，
# 并从`BaseSettings` 继承了"从环境变量读取 + 类型验证"的核心能力——这是整个配置模块的主体结构，
# 后续所有配置字段都会写在这个类里面。
class Settings(BaseSettings):
    """应用配置类——自动从 .env 文件和系统环境变量读取"""
 
    # ===== 应用基础 =====
    app_name: str = "AI Chat API"
    app_version: str = "0.1.0"
    environment: str = "development"  # development / production
    log_level: str = "INFO"

    # ===== 服务器 =====
    host: str = "0.0.0.0"
    port: int = 8000

    # ===== DeepSeek 配置 =====
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-v4-flash"
 
    # ===== OpenAI 配置 =====
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-5.6-luna"

    # ===== 服务限制 =====
    max_tokens_default: int = 4096
    request_timeout: int = 60  # 秒

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        # "case_sensitive": True, # 区分大小写
    }
    
    #`@property` 把方法`is_development` 伪装成一个"只读属性"，
    # 让你能用`settings.is_development` 这种简洁语法，实时判断当前是否处于开发模式，
    # 同时避免了手动维护一个可能不一致的布尔字段。
    @property 
    # 计算属性，根据环境判断是否为开发模式
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def available_models(self) -> list[dict]:
        """返回当前已配置的可用模型列表"""
        models = []
        if self.deepseek_api_key:
            models.append({
                "id": "deepseek",
                "name": "DeepSeek-V4-flash",
                "provider": "DeepSeek",
                "description": "高性价比通用模型，中文能力强",
            })
        if self.openai_api_key:
            models.append({
                "id": "openai",
                "name": self.openai_model,
                "provider": "OpenAI",
                "description": "综合能力最强的模型之一",
            })
        return models


# 全局单例——用 lru_cache 保证只初始化一次
@lru_cache()
def get_settings() -> Settings:
    return Settings()


