"""
用户相关数据模式
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field

from .common import BaseResponse


class UserBase(BaseModel):
    """
    用户基础模型
    """
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    full_name: Optional[str] = Field(default=None, max_length=100, description="真实姓名")
    institution: Optional[str] = Field(default=None, max_length=200, description="所属机构")
    title: Optional[str] = Field(default=None, max_length=100, description="职称")
    specialty: Optional[str] = Field(default=None, max_length=200, description="专业领域")
    
    class Config:
        from_attributes = True


class UserCreate(UserBase):
    """
    用户创建模型
    """
    password: str = Field(..., min_length=8, max_length=255, description="密码")


class UserUpdate(BaseModel):
    """
    用户更新模型
    """
    full_name: Optional[str] = Field(default=None, max_length=100, description="真实姓名")
    institution: Optional[str] = Field(default=None, max_length=200, description="所属机构")
    title: Optional[str] = Field(default=None, max_length=100, description="职称")
    specialty: Optional[str] = Field(default=None, max_length=200, description="专业领域")
    
    class Config:
        from_attributes = True


class UserResponse(UserBase):
    """
    用户响应模型
    """
    id: str = Field(..., description="用户ID")
    is_active: bool = Field(default=True, description="是否激活")
    is_verified: bool = Field(default=False, description="是否验证")
    is_superuser: bool = Field(default=False, description="是否超级用户")
    last_login: Optional[datetime] = Field(default=None, description="最后登录时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(default=None, description="更新时间")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserLogin(BaseModel):
    """
    用户登录模型
    """
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")


class TokenResponse(BaseResponse):
    """
    Token响应模型
    """
    data: Dict[str, Any] = Field(default_factory=dict, description="响应数据")
    
    @classmethod
    def create(
        cls,
        access_token: str,
        token_type: str = "bearer",
        expires_in: int = 480,
        user: Optional[Dict[str, Any]] = None
    ) -> "TokenResponse":
        """
        创建Token响应
        """
        return cls(
            data={
                "access_token": access_token,
                "token_type": token_type,
                "expires_in": expires_in,
                "user": user
            }
        )


class UserFavoriteResponse(BaseModel):
    """
    用户收藏响应模型
    """
    id: str = Field(..., description="收藏ID")
    study_id: str = Field(..., description="研究ID")
    study_title: str = Field(..., description="研究标题")
    created_at: datetime = Field(..., description="收藏时间")
    
    class Config:
        from_attributes = True


class UserHistoryResponse(BaseModel):
    """
    浏览历史响应模型
    """
    id: str = Field(..., description="历史ID")
    study_id: str = Field(..., description="研究ID")
    study_title: str = Field(..., description="研究标题")
    viewed_at: datetime = Field(..., description="浏览时间")
    
    class Config:
        from_attributes = True


class SearchHistoryResponse(BaseModel):
    """
    搜索历史响应模型
    """
    id: str = Field(..., description="历史ID")
    query: str = Field(..., description="搜索关键词")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="筛选条件")
    result_count: Optional[int] = Field(default=None, description="结果数量")
    created_at: datetime = Field(..., description="搜索时间")
    
    class Config:
        from_attributes = True


class UserFeedbackCreate(BaseModel):
    """
    用户反馈创建模型
    """
    study_id: Optional[str] = Field(default=None, description="研究ID")
    feedback_type: Optional[str] = Field(default=None, description="反馈类型")
    feedback_text: str = Field(..., min_length=10, description="反馈内容")


class UserFeedbackResponse(BaseModel):
    """
    用户反馈响应模型
    """
    id: str = Field(..., description="反馈ID")
    user_id: Optional[str] = Field(default=None, description="用户ID")
    study_id: Optional[str] = Field(default=None, description="研究ID")
    feedback_type: Optional[str] = Field(default=None, description="反馈类型")
    feedback_text: str = Field(..., description="反馈内容")
    status: str = Field(default="pending", description="反馈状态")
    response_text: Optional[str] = Field(default=None, description="回复内容")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(default=None, description="更新时间")
    
    class Config:
        from_attributes = True


class PasswordChangeRequest(BaseModel):
    """
    密码修改请求模型
    """
    current_password: str = Field(..., description="当前密码")
    new_password: str = Field(..., min_length=8, description="新密码")


class PasswordResetRequest(BaseModel):
    """
    密码重置请求模型
    """
    email: EmailStr = Field(..., description="注册邮箱")