"""
日志配置模块
"""

import logging
import sys
from typing import Optional

from loguru import logger

from app.core.config import settings


class InterceptHandler(logging.Handler):
    """
    日志拦截处理器
    """
    
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging() -> None:
    """
    设置日志配置
    """
    # 移除默认处理器
    logger.remove()
    
    # 控制台输出
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        colorize=True
    )
    
    # 文件输出（如果配置了日志文件）
    if settings.LOG_FILE:
        logger.add(
            settings.LOG_FILE,
            level=settings.LOG_LEVEL,
            format="{time:YYYY-MM-DD HH:mm:ss} | "
                   "{level: <8} | "
                   "{name}:{function}:{line} - "
                   "{message}",
            rotation="00:00",
            retention="30 days",
            compression="zip"
        )
    
    # 拦截标准日志
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # 设置第三方库的日志级别
    logging.getLogger("uvicorn").handlers = [InterceptHandler()]
    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)