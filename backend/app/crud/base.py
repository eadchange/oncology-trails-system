"""
CRUD基础类
提供通用的数据库操作方法
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import RelationshipProperty

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    CRUD基础类
    """

    def __init__(self, model: Type[ModelType]):
        """
        CRUD对象初始化
        
        Args:
            model: SQLAlchemy模型类
        """
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """
        根据ID获取单个对象
        
        Args:
            db: 数据库会话
            id: 对象ID
            
        Returns:
            模型对象或None
        """
        stmt = select(self.model).where(self.model.id == id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None
    ) -> List[ModelType]:
        """
        获取多个对象（支持分页和筛选）
        
        Args:
            db: 数据库会话
            skip: 跳过的记录数
            limit: 返回的记录数
            filters: 筛选条件字典
            order_by: 排序字段
            
        Returns:
            模型对象列表
        """
        stmt = select(self.model)
        
        # 添加筛选条件
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    stmt = stmt.where(getattr(self.model, key) == value)
        
        # 添加排序
        if order_by and hasattr(self.model, order_by):
            stmt = stmt.order_by(getattr(self.model, order_by).desc())
        
        # 添加分页
        stmt = stmt.offset(skip).limit(limit)
        
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """
        创建新对象
        
        Args:
            db: 数据库会话
            obj_in: 创建数据
            
        Returns:
            创建的模型对象
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        更新对象
        
        Args:
            db: 数据库会话
            db_obj: 数据库中的对象
            obj_in: 更新数据
            
        Returns:
            更新后的模型对象
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: Any) -> Optional[ModelType]:
        """
        删除对象（软删除）
        
        Args:
            db: 数据库会话
            id: 对象ID
            
        Returns:
            删除的模型对象或None
        """
        obj = await self.get(db, id)
        if obj:
            if hasattr(obj, 'is_active'):
                # 软删除
                obj.is_active = False
                db.add(obj)
                await db.commit()
                await db.refresh(obj)
            else:
                # 硬删除
                await db.delete(obj)
                await db.commit()
        return obj

    async def count(
        self,
        db: AsyncSession,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        统计记录数
        
        Args:
            db: 数据库会话
            filters: 筛选条件
            
        Returns:
            记录总数
        """
        stmt = select(func.count(self.model.id))
        
        # 添加筛选条件
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    stmt = stmt.where(getattr(self.model, key) == value)
        
        result = await db.execute(stmt)
        return result.scalar()

    async def get_by_field(
        self,
        db: AsyncSession,
        field: str,
        value: Any
    ) -> Optional[ModelType]:
        """
        根据字段值获取单个对象
        
        Args:
            db: 数据库会话
            field: 字段名
            value: 字段值
            
        Returns:
            模型对象或None
        """
        if not hasattr(self.model, field):
            return None
        
        stmt = select(self.model).where(getattr(self.model, field) == value)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_by_field(
        self,
        db: AsyncSession,
        field: str,
        value: Any,
        order_by: Optional[str] = None
    ) -> List[ModelType]:
        """
        根据字段值获取所有对象
        
        Args:
            db: 数据库会话
            field: 字段名
            value: 字段值
            order_by: 排序字段
            
        Returns:
            模型对象列表
        """
        if not hasattr(self.model, field):
            return []
        
        stmt = select(self.model).where(getattr(self.model, field) == value)
        
        # 添加排序
        if order_by and hasattr(self.model, order_by):
            stmt = stmt.order_by(getattr(self.model, order_by).desc())
        
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def exists(self, db: AsyncSession, id: Any) -> bool:
        """
        检查对象是否存在
        
        Args:
            db: 数据库会话
            id: 对象ID
            
        Returns:
            是否存在
        """
        stmt = select(func.count(self.model.id)).where(self.model.id == id)
        result = await db.execute(stmt)
        return result.scalar() > 0

    async def bulk_create(self, db: AsyncSession, *, objs_in: List[CreateSchemaType]) -> List[ModelType]:
        """
        批量创建对象
        
        Args:
            db: 数据库会话
            objs_in: 创建数据列表
            
        Returns:
            创建的模型对象列表
        """
        db_objs = []
        for obj_in in objs_in:
            obj_in_data = jsonable_encoder(obj_in)
            db_obj = self.model(**obj_in_data)
            db_objs.append(db_obj)
        
        db.add_all(db_objs)
        await db.commit()
        
        for db_obj in db_objs:
            await db.refresh(db_obj)
        
        return db_objs