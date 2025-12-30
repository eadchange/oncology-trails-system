"""
用户相关数据模型
"""

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Boolean, 
    Date, 
    DateTime, 
    ForeignKey, 
    Integer, 
    JSONB,
    String, 
    Text,
    UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class User(Base):
    """
    用户表
    """
    
    __tablename__ = "users"
    
    # 基本信息
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="用户名")
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment="邮箱")
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False, comment="密码哈希")
    
    # 个人资料
    full_name: Mapped[Optional[str]] = mapped_column(String(100), comment="真实姓名")
    institution: Mapped[Optional[str]] = mapped_column(String(200), comment="所属机构")
    title: Mapped[Optional[str]] = mapped_column(String(100), comment="职称")
    specialty: Mapped[Optional[str]] = mapped_column(String(200), comment="专业领域")
    
    # 状态字段
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否激活")
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否验证")
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否超级用户")
    
    # 登录信息
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), comment="最后登录时间")
    
    # 关系
    roles = relationship("Role", secondary="user_roles", back_populates="users")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    favorites = relationship("UserFavorite", back_populates="user", cascade="all, delete-orphan")
    history = relationship("UserHistory", back_populates="user", cascade="all, delete-orphan")
    search_history = relationship("SearchHistory", back_populates="user", cascade="all, delete-orphan")
    feedback = relationship("UserFeedback", back_populates="user", cascade="all, delete-orphan")


class Role(Base):
    """
    用户角色表
    """
    
    __tablename__ = "roles"
    
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="角色名称")
    description: Mapped[Optional[str]] = mapped_column(Text, comment="角色描述")
    permissions: Mapped[Optional[dict]] = mapped_column(JSONB, default={}, comment="权限配置")
    
    # 关系
    users = relationship("User", secondary="user_roles", back_populates="roles")


class UserRole(Base):
    """
    用户角色关联表
    """
    
    __tablename__ = "user_roles"
    
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    role_id: Mapped[str] = mapped_column(ForeignKey("roles.id"), primary_key=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()", comment="分配时间")
    assigned_by: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), comment="分配人")
    
    # 关系
    user = relationship("User", foreign_keys=[user_id])
    role = relationship("Role")


class UserSession(Base):
    """
    用户会话表
    """
    
    __tablename__ = "user_sessions"
    
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    session_token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, comment="会话令牌")
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), comment="IP地址")
    user_agent: Mapped[Optional[str]] = mapped_column(Text, comment="用户代理")
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, comment="过期时间")
    
    # 关系
    user = relationship("User", back_populates="sessions")


class UserFavorite(Base):
    """
    用户收藏表
    """
    
    __tablename__ = "user_favorites"
    
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    study_id: Mapped[str] = mapped_column(ForeignKey("studies.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()", comment="收藏时间")
    
    # 复合唯一约束
    __table_args__ = (UniqueConstraint('user_id', 'study_id', name='uq_user_favorite'),)
    
    # 关系
    user = relationship("User", back_populates="favorites")
    # study关系在clinical_trial.py中定义


class UserHistory(Base):
    """
    浏览历史表
    """
    
    __tablename__ = "user_history"
    
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    study_id: Mapped[str] = mapped_column(ForeignKey("studies.id"), nullable=False)
    viewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()", comment="浏览时间")
    
    # 关系
    user = relationship("User", back_populates="history")
    # study关系在clinical_trial.py中定义


class SearchHistory(Base):
    """
    搜索历史表
    """
    
    __tablename__ = "search_history"
    
    user_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), comment="用户ID（可选）")
    query: Mapped[str] = mapped_column(Text, nullable=False, comment="搜索关键词")
    filters: Mapped[Optional[dict]] = mapped_column(JSONB, default={}, comment="筛选条件")
    result_count: Mapped[Optional[int]] = mapped_column(Integer, comment="结果数量")
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()", comment="搜索时间")
    
    # 关系
    user = relationship("User", back_populates="search_history")


class UserFeedback(Base):
    """
    用户反馈表
    """
    
    __tablename__ = "user_feedback"
    
    user_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), comment="用户ID（可选）")
    study_id: Mapped[Optional[str]] = mapped_column(ForeignKey("studies.id"), comment="研究ID（可选）")
    
    feedback_type: Mapped[Optional[str]] = mapped_column(String(50), comment="反馈类型")
    feedback_text: Mapped[str] = mapped_column(Text, nullable=False, comment="反馈内容")
    
    # 反馈状态
    status: Mapped[str] = mapped_column(String(50), default="pending", comment="反馈状态")
    
    # 处理信息
    assigned_to: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), comment="处理人")
    response_text: Mapped[Optional[str]] = mapped_column(Text, comment="回复内容")
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), comment="解决时间")
    
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate="now()", comment="更新时间")
    
    # 关系
    user = relationship("User", foreign_keys=[user_id], back_populates="feedback")
    assigned_user = relationship("User", foreign_keys=[assigned_to])