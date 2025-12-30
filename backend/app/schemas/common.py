"""
通用数据模式
"""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    """
    基础响应模型
    """
    code: int = Field(default=200, description="响应代码")
    message: str = Field(default="success", description="响应消息")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ErrorResponse(BaseResponse):
    """
    错误响应模型
    """
    code: int = Field(default=400, description="错误代码")
    message: str = Field(default="error", description="错误消息")
    errors: Optional[Dict[str, Any]] = Field(default=None, description="详细错误信息")


T = TypeVar("T")


class PaginatedResponse(BaseResponse, Generic[T]):
    """
    分页响应模型
    """
    data: Dict[str, Any] = Field(default_factory=dict, description="响应数据")
    
    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        size: int,
        **kwargs
    ) -> "PaginatedResponse[T]":
        """
        创建分页响应
        """
        return cls(
            data={
                "items": items,
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size,
                **kwargs
            }
        )


class PaginationParams(BaseModel):
    """
    分页参数
    """
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=20, ge=1, le=100, description="每页数量")
    
    @property
    def offset(self) -> int:
        """计算偏移量"""
        return (self.page - 1) * self.size


class SortParams(BaseModel):
    """
    排序参数
    """
    sort_by: Optional[str] = Field(default=None, description="排序字段")
    sort_order: str = Field(default="desc", regex="^(asc|desc)$", description="排序顺序")


class FilterParams(BaseModel):
    """
    筛选参数基类
    """
    pass


class SearchParams(BaseModel):
    """
    搜索参数
    """
    q: Optional[str] = Field(default=None, description="搜索关键词")
    include_fields: Optional[List[str]] = Field(default=None, description="包含字段")
    exclude_fields: Optional[List[str]] = Field(default=None, description="排除字段")