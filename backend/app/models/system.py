"""
系统相关数据模型
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
    Inet
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class SystemConfig(Base):
    """
    系统配置表
    """
    
    __tablename__ = "system_configs"
    
    config_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment="配置键")
    config_value: Mapped[Optional[str]] = mapped_column(Text, comment="配置值")
    config_type: Mapped[Optional[str]] = mapped_column(String(50), comment="配置类型")
    description: Mapped[Optional[str]] = mapped_column(Text, comment="配置描述")
    is_editable: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否可编辑")


class SystemLog(Base):
    """
    系统日志表
    """
    
    __tablename__ = "system_logs"
    
    user_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), comment="用户ID")
    action: Mapped[str] = mapped_column(String(100), nullable=False, comment="操作动作")
    resource_type: Mapped[Optional[str]] = mapped_column(String(100), comment="资源类型")
    resource_id: Mapped[Optional[str]] = mapped_column(String(100), comment="资源ID")
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), comment="IP地址")
    user_agent: Mapped[Optional[str]] = mapped_column(Text, comment="用户代理")
    request_data: Mapped[Optional[dict]] = mapped_column(JSONB, comment="请求数据")
    response_data: Mapped[Optional[dict]] = mapped_column(JSONB, comment="响应数据")
    error_message: Mapped[Optional[str]] = mapped_column(Text, comment="错误信息")
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, comment="处理时间（毫秒）")


class DataSyncLog(Base):
    """
    数据同步日志表
    """
    
    __tablename__ = "data_sync_logs"
    
    data_source: Mapped[str] = mapped_column(String(100), nullable=False, comment="数据源")
    sync_type: Mapped[Optional[str]] = mapped_column(String(50), comment="同步类型")
    
    # 同步统计
    total_records: Mapped[Optional[int]] = mapped_column(Integer, comment="总记录数")
    new_records: Mapped[Optional[int]] = mapped_column(Integer, comment="新增记录数")
    updated_records: Mapped[Optional[int]] = mapped_column(Integer, comment="更新记录数")
    deleted_records: Mapped[Optional[int]] = mapped_column(Integer, comment="删除记录数")
    error_records: Mapped[Optional[int]] = mapped_column(Integer, comment="错误记录数")
    
    # 时间信息
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), comment="开始时间")
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), comment="结束时间")
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, comment="持续时间（秒）")
    
    # 状态
    status: Mapped[Optional[str]] = mapped_column(String(50), comment="同步状态")
    error_message: Mapped[Optional[str]] = mapped_column(Text, comment="错误信息")