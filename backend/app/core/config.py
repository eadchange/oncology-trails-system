"""
系统配置模块
包含所有环境变量的配置和验证
"""

import os
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    应用配置类
    支持从环境变量读取配置
    """
    
    # 应用基本信息
    APP_NAME: str = "肿瘤治疗进展查询系统"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "专业的肿瘤临床研究进展查询平台"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    # 数据库配置
    DATABASE_URL: Optional[PostgresDsn] = None
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "password"
    DB_NAME: str = "oncology_db"
    
    # Redis配置
    REDIS_URL: Optional[str] = None
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    
    # Elasticsearch配置
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    ELASTICSEARCH_INDEX: str = "clinical_trials"
    
    # JWT配置
    JWT_SECRET_KEY: str = "your-secret-key-here"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8小时
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-here"
    PASSWORD_MIN_LENGTH: int = 8
    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_LOCKOUT_MINUTES: int = 30
    
    # 分页配置
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # 搜索配置
    MAX_SEARCH_RESULTS: int = 1000
    SEARCH_TIMEOUT_SECONDS: int = 30
    
    # 缓存配置
    CACHE_TTL_SECONDS: int = 1800  # 30分钟
    HOT_DATA_CACHE_TTL: int = 300  # 5分钟
    
    # 数据同步配置
    DATA_SYNC_INTERVAL_HOURS: int = 24
    CLINICALTRIALS_API_URL: str = "https://clinicaltrials.gov/api/v2"
    PUBMED_API_URL: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = None
    
    # CORS配置
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    ALLOWED_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE"]
    ALLOWED_HEADERS: List[str] = ["*"]
    
    # 监控配置
    ENABLE_METRICS: bool = True
    METRICS_ENDPOINT: str = "/metrics"
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        """组装数据库连接字符串"""
        if isinstance(v, str):
            return v
        
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.get("DB_USER"),
            password=values.get("DB_PASSWORD"),
            host=values.get("DB_HOST"),
            port=values.get("DB_PORT"),
            path=f"/{values.get('DB_NAME')}",
        )
    
    @field_validator("REDIS_URL", mode="before")
    @classmethod
    def assemble_redis_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        """组装Redis连接字符串"""
        if isinstance(v, str):
            return v
        
        password = values.get("REDIS_PASSWORD")
        auth = f":{password}@" if password else ""
        
        return f"redis://{auth}{values.get('REDIS_HOST')}:{values.get('REDIS_PORT')}/{values.get('REDIS_DB')}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    获取配置实例（使用缓存避免重复读取）
    """
    return Settings()


# 全局配置实例
settings = get_settings()