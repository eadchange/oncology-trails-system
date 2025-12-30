"""
基础模型类
"""

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import DateTime, func
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Mapped, mapped_column
import uuid


@as_declarative()
class Base:
    """
    所有模型的基类
    """
    
    id: Any
    __name__: str
    
    # 自动生成表名
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    
    # 创建时间
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="创建时间"
    )
    
    # 更新时间
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        comment="更新时间"
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """将模型转换为字典"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if value is not None:
                result[column.name] = value
        return result
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"<{self.__class__.__name__}(id={self.id})>"