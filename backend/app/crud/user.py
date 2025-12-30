"""
用户相关CRUD操作
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User, UserRole, UserSession, UserFavorite, UserHistory, UserFeedback
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """
    用户的CRUD操作
    """
    
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """
        根据邮箱获取用户
        """
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """
        根据用户名获取用户
        """
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def authenticate(
        self,
        db: AsyncSession,
        username: str,
        password: str
    ) -> Optional[User]:
        """
        用户认证
        
        Args:
            db: 数据库会话
            username: 用户名或邮箱
            password: 密码
            
        Returns:
            认证成功的用户或None
        """
        # 尝试通过用户名登录
        user = await self.get_by_username(db, username)
        if not user:
            # 尝试通过邮箱登录
            user = await self.get_by_email(db, username)
        
        if not user:
            return None
        
        if not user.is_active:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        return user
    
    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        """
        创建用户
        """
        # 密码加密
        password_hash = get_password_hash(obj_in.password)
        
        # 创建用户对象
        db_obj = User(
            username=obj_in.username,
            email=obj_in.email,
            password_hash=password_hash,
            full_name=obj_in.full_name,
            institution=obj_in.institution,
            title=obj_in.title,
            specialty=obj_in.specialty
        )
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update_last_login(self, db: AsyncSession, *, user_id: str) -> None:
        """
        更新用户最后登录时间
        """
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(last_login=datetime.now())
        )
        await db.execute(stmt)
        await db.commit()
    
    async def is_superuser(self, db: AsyncSession, user_id: str) -> bool:
        """
        检查用户是否为超级用户
        """
        user = await self.get(db, user_id)
        return user.is_superuser if user else False
    
    async def change_password(
        self,
        db: AsyncSession,
        user_id: str,
        new_password: str
    ) -> bool:
        """
        修改用户密码
        """
        password_hash = get_password_hash(new_password)
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(password_hash=password_hash)
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount > 0


class CRUDUserSession(CRUDBase[UserSession, Any, Any]):
    """
    用户会话的CRUD操作
    """
    
    async def create_session(
        self,
        db: AsyncSession,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> UserSession:
        """
        创建用户会话
        """
        import uuid
        
        session_token = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        db_obj = UserSession(
            user_id=user_id,
            session_token=session_token,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at
        )
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_by_token(self, db: AsyncSession, token: str) -> Optional[UserSession]:
        """
        根据令牌获取会话
        """
        stmt = select(UserSession).where(
            UserSession.session_token == token,
            UserSession.expires_at > datetime.now()
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def expire_session(self, db: AsyncSession, token: str) -> bool:
        """
        使会话过期
        """
        stmt = (
            update(UserSession)
            .where(UserSession.session_token == token)
            .values(expires_at=datetime.now())
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount > 0
    
    async def cleanup_expired_sessions(self, db: AsyncSession) -> int:
        """
        清理过期会话
        """
        stmt = (
            select(UserSession)
            .where(UserSession.expires_at <= datetime.now())
        )
        result = await db.execute(stmt)
        expired_sessions = result.scalars().all()
        
        for session in expired_sessions:
            await db.delete(session)
        
        await db.commit()
        return len(expired_sessions)


class CRUDUserFavorite(CRUDBase[UserFavorite, Any, Any]):
    """
    用户收藏的CRUD操作
    """
    
    async def add_favorite(self, db: AsyncSession, user_id: str, study_id: str) -> Optional[UserFavorite]:
        """
        添加收藏
        """
        # 检查是否已收藏
        stmt = select(UserFavorite).where(
            UserFavorite.user_id == user_id,
            UserFavorite.study_id == study_id
        )
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            return None
        
        # 创建收藏
        db_obj = UserFavorite(user_id=user_id, study_id=study_id)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def remove_favorite(self, db: AsyncSession, user_id: str, study_id: str) -> bool:
        """
        移除收藏
        """
        stmt = select(UserFavorite).where(
            UserFavorite.user_id == user_id,
            UserFavorite.study_id == study_id
        )
        result = await db.execute(stmt)
        favorite = result.scalar_one_or_none()
        
        if favorite:
            await db.delete(favorite)
            await db.commit()
            return True
        
        return False
    
    async def get_user_favorites(
        self,
        db: AsyncSession,
        user_id: str,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[UserFavorite], int]:
        """
        获取用户收藏列表
        """
        stmt = select(UserFavorite).where(UserFavorite.user_id == user_id)
        
        # 统计总数
        count_stmt = select(func.count(UserFavorite.id)).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar()
        
        # 分页
        offset = (page - 1) * size
        stmt = stmt.offset(offset).limit(size).order_by(UserFavorite.created_at.desc())
        
        result = await db.execute(stmt)
        favorites = list(result.scalars().all())
        
        return favorites, total
    
    async def is_favorited(self, db: AsyncSession, user_id: str, study_id: str) -> bool:
        """
        检查是否已收藏
        """
        stmt = select(UserFavorite).where(
            UserFavorite.user_id == user_id,
            UserFavorite.study_id == study_id
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None


class CRUDUserHistory(CRUDBase[UserHistory, Any, Any]):
    """
    用户浏览历史的CRUD操作
    """
    
    async def add_history(self, db: AsyncSession, user_id: str, study_id: str) -> UserHistory:
        """
        添加浏览历史
        """
        db_obj = UserHistory(user_id=user_id, study_id=study_id)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_user_history(
        self,
        db: AsyncSession,
        user_id: str,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[UserHistory], int]:
        """
        获取用户浏览历史
        """
        stmt = select(UserHistory).where(UserHistory.user_id == user_id)
        
        # 统计总数
        count_stmt = select(func.count(UserHistory.id)).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar()
        
        # 分页
        offset = (page - 1) * size
        stmt = stmt.offset(offset).limit(size).order_by(UserHistory.viewed_at.desc())
        
        result = await db.execute(stmt)
        history = list(result.scalars().all())
        
        return history, total
    
    async def clear_history(self, db: AsyncSession, user_id: str) -> int:
        """
        清空用户浏览历史
        """
        stmt = select(UserHistory).where(UserHistory.user_id == user_id)
        result = await db.execute(stmt)
        history_items = result.scalars().all()
        
        for item in history_items:
            await db.delete(item)
        
        await db.commit()
        return len(history_items)


class CRUDSearchHistory(CRUDBase[SearchHistory, Any, Any]):
    """
    搜索历史的CRUD操作
    """
    
    async def add_search(
        self,
        db: AsyncSession,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        result_count: Optional[int] = None,
        user_id: Optional[str] = None
    ) -> SearchHistory:
        """
        添加搜索历史
        """
        db_obj = SearchHistory(
            user_id=user_id,
            query=query,
            filters=filters,
            result_count=result_count
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_user_search_history(
        self,
        db: AsyncSession,
        user_id: str,
        limit: int = 20
    ) -> List[SearchHistory]:
        """
        获取用户搜索历史
        """
        stmt = select(SearchHistory).where(
            SearchHistory.user_id == user_id
        ).order_by(SearchHistory.created_at.desc()).limit(limit)
        
        result = await db.execute(stmt)
        return list(result.scalars().all())


class CRUDUserFeedback(CRUDBase[UserFeedback, Any, Any]):
    """
    用户反馈的CRUD操作
    """
    
    async def get_feedback_list(
        self,
        db: AsyncSession,
        status: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[UserFeedback], int]:
        """
        获取反馈列表
        """
        stmt = select(UserFeedback)
        
        if status:
            stmt = stmt.where(UserFeedback.status == status)
        
        # 统计总数
        count_stmt = select(func.count(UserFeedback.id)).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar()
        
        # 分页
        offset = (page - 1) * size
        stmt = stmt.offset(offset).limit(size).order_by(UserFeedback.created_at.desc())
        
        result = await db.execute(stmt)
        feedback_list = list(result.scalars().all())
        
        return feedback_list, total
    
    async def update_status(
        self,
        db: AsyncSession,
        feedback_id: str,
        status: str,
        response_text: Optional[str] = None,
        assigned_to: Optional[str] = None
    ) -> Optional[UserFeedback]:
        """
        更新反馈状态
        """
        feedback = await self.get(db, feedback_id)
        if not feedback:
            return None
        
        feedback.status = status
        if response_text:
            feedback.response_text = response_text
        if assigned_to:
            feedback.assigned_to = assigned_to
        
        db.add(feedback)
        await db.commit()
        await db.refresh(feedback)
        return feedback


# 创建CRUD实例
user = CRUDUser(User)
user_session = CRUDUserSession(UserSession)
user_favorite = CRUDUserFavorite(UserFavorite)
user_history = CRUDUserHistory(UserHistory)
search_history = CRUDSearchHistory(SearchHistory)
user_feedback = CRUDUserFeedback(UserFeedback)