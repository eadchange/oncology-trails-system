"""
依赖注入模块
"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.core.config import settings
from app.core.security import verify_token
from app.db.base import get_db
from app.schemas.user import UserResponse

# 安全方案
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[UserResponse]:
    """
    获取当前登录用户（可选）
    
    Args:
        credentials: HTTP认证凭证
        db: 数据库会话
        
    Returns:
        当前用户或None
    """
    if not credentials:
        return None
    
    try:
        # 验证令牌
        payload = verify_token(credentials.credentials)
        if not payload:
            return None
        
        # 获取用户ID
        user_id: str = payload.get("sub")
        if not user_id:
            return None
        
        # 获取用户信息
        user = await crud.user.get(db, user_id)
        if not user or not user.is_active:
            return None
        
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            institution=user.institution,
            title=user.title,
            specialty=user.specialty,
            is_active=user.is_active,
            is_verified=user.is_verified,
            is_superuser=user.is_superuser,
            last_login=user.last_login,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except Exception:
        return None


async def get_current_user_required(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    获取当前登录用户（必需）
    
    Args:
        credentials: HTTP认证凭证
        db: 数据库会话
        
    Returns:
        当前用户
        
    Raises:
        HTTPException: 未认证或用户不存在
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # 验证令牌
        payload = verify_token(credentials.credentials)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证凭证",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 获取用户ID
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证凭证",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 获取用户信息
        user = await crud.user.get(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户已被禁用"
            )
        
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            institution=user.institution,
            title=user.title,
            specialty=user.specialty,
            is_active=user.is_active,
            is_verified=user.is_verified,
            is_superuser=user.is_superuser,
            last_login=user.last_login,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证失败",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_superuser(
    current_user: UserResponse = Depends(get_current_user_required)
) -> UserResponse:
    """
    获取当前超级用户
    
    Args:
        current_user: 当前用户
        
    Returns:
        超级用户
        
    Raises:
        HTTPException: 不是超级用户
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要超级用户权限"
        )
    return current_user


def create_pagination_params(
    page: int = 1,
    size: int = 20
) -> dict:
    """
    创建分页参数
    
    Args:
        page: 页码
        size: 每页数量
        
    Returns:
        分页参数字典
    """
    return {
        "page": page,
        "size": size,
        "offset": (page - 1) * size
    }


def create_sort_params(
    sort_by: Optional[str] = None,
    sort_order: str = "desc"
) -> dict:
    """
    创建排序参数
    
    Args:
        sort_by: 排序字段
        sort_order: 排序方向
        
    Returns:
        排序参数字典
    """
    return {
        "sort_by": sort_by,
        "sort_order": sort_order
    }