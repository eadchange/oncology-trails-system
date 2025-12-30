"""
用户相关API端点
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.api.deps import get_db, get_current_user
from app.core.config import settings
from app.core.security import (
    create_access_token,
    verify_token,
    validate_password,
    verify_password
)
from app.schemas.common import ErrorResponse
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserLogin,
    TokenResponse,
    UserUpdate,
    PasswordChangeRequest,
    UserFavoriteResponse,
    UserHistoryResponse,
    SearchHistoryResponse,
    UserFeedbackCreate,
    UserFeedbackResponse
)

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=UserResponse, summary="用户注册")
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    用户注册
    """
    try:
        # 检查用户名是否已存在
        user = await crud.user.get_by_username(db, user_in.username)
        if user:
            return ErrorResponse(
                code=400,
                message="用户名已存在"
            )
        
        # 检查邮箱是否已存在
        user = await crud.user.get_by_email(db, user_in.email)
        if user:
            return ErrorResponse(
                code=400,
                message="邮箱已注册"
            )
        
        # 验证密码强度
        if not validate_password(user_in.password):
            return ErrorResponse(
                code=400,
                message="密码强度不足，需要至少8位并包含数字和字母"
            )
        
        # 创建用户
        user = await crud.user.create(db, obj_in=user_in)
        
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
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except Exception as e:
        return ErrorResponse(
            code=500,
            message=f"注册失败: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse, summary="用户登录")
async def login(
    user_in: UserLogin,
    response: Response,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    用户登录
    """
    try:
        # 用户认证
        user = await crud.user.authenticate(db, user_in.username, user_in.password)
        if not user:
            return ErrorResponse(
                code=401,
                message="用户名或密码错误"
            )
        
        # 更新最后登录时间
        await crud.user.update_last_login(db, user_id=user.id)
        
        # 创建访问令牌
        access_token = create_access_token(
            data={"sub": user.id, "username": user.username, "email": user.email}
        )
        
        # 创建会话
        session = await crud.user_session.create_session(
            db=db,
            user_id=user.id,
            ip_address=None,  # 可以从request中获取
            user_agent=None   # 可以从request中获取
        )
        
        # 设置Cookie
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
        return TokenResponse.create(
            access_token=access_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user={
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "institution": user.institution,
                "title": user.title,
                "specialty": user.specialty
            }
        )
        
    except Exception as e:
        return ErrorResponse(
            code=500,
            message=f"登录失败: {str(e)}"
        )


@router.post("/logout", summary="用户登出")
async def logout(
    response: Response,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    用户登出
    """
    try:
        # 验证令牌
        token = credentials.credentials
        payload = verify_token(token)
        
        if payload:
            # 使会话过期
            await crud.user_session.expire_session(db, token)
        
        # 清除Cookie
        response.delete_cookie("access_token")
        
        return {"message": "登出成功"}
        
    except Exception as e:
        return ErrorResponse(
            code=500,
            message=f"登出失败: {str(e)}"
        )


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_current_user_info(
    current_user: UserResponse = Depends(get_current_user)
) -> Any:
    """
    获取当前登录用户信息
    """
    return current_user


@router.put("/me", response_model=UserResponse, summary="更新当前用户信息")
async def update_current_user(
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
) -> Any:
    """
    更新当前用户信息
    """
    try:
        # 获取用户对象
        user = await crud.user.get(db, current_user.id)
        if not user:
            return ErrorResponse(
                code=404,
                message="用户不存在"
            )
        
        # 更新用户信息
        user = await crud.user.update(db, db_obj=user, obj_in=user_in)
        
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
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except Exception as e:
        return ErrorResponse(
            code=500,
            message=f"更新用户信息失败: {str(e)}"
        )


@router.post("/change-password", summary="修改密码")
async def change_password(
    password_in: PasswordChangeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
) -> Any:
    """
    修改用户密码
    """
    try:
        # 获取用户对象
        user = await crud.user.get(db, current_user.id)
        if not user:
            return ErrorResponse(
                code=404,
                message="用户不存在"
            )
        
        # 验证当前密码
        if not verify_password(password_in.current_password, user.password_hash):
            return ErrorResponse(
                code=400,
                message="当前密码错误"
            )
        
        # 验证新密码强度
        if not validate_password(password_in.new_password):
            return ErrorResponse(
                code=400,
                message="密码强度不足，需要至少8位并包含数字和字母"
            )
        
        # 修改密码
        success = await crud.user.change_password(db, user.id, password_in.new_password)
        
        if success:
            return {"message": "密码修改成功"}
        else:
            return ErrorResponse(
                code=500,
                message="密码修改失败"
            )
        
    except Exception as e:
        return ErrorResponse(
            code=500,
            message=f"修改密码失败: {str(e)}"
        )


@router.get("/favorites", response_model=Dict[str, Any], summary="获取用户收藏")
async def get_user_favorites(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
) -> Any:
    """
    获取用户收藏的研究
    """
    try:
        favorites, total = await crud.user_favorite.get_user_favorites(
            db=db,
            user_id=current_user.id,
            page=page,
            size=size
        )
        
        # 获取研究详情
        favorite_responses = []
        for favorite in favorites:
            study = await crud.study.get(db, favorite.study_id)
            if study:
                favorite_responses.append(
                    UserFavoriteResponse(
                        id=favorite.id,
                        study_id=study.id,
                        study_title=study.official_title,
                        created_at=favorite.created_at
                    )
                )
        
        return {
            "items": favorite_responses,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
        
    except Exception as e:
        return ErrorResponse(
            code=500,
            message=f"获取收藏失败: {str(e)}"
        )


@router.post("/favorites/{study_id}", summary="添加收藏")
async def add_favorite(
    study_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
) -> Any:
    """
    添加研究到收藏
    """
    try:
        # 检查研究是否存在
        study = await crud.study.get(db, study_id)
        if not study:
            return ErrorResponse(
                code=404,
                message="研究不存在"
            )
        
        # 添加收藏
        favorite = await crud.user_favorite.add_favorite(db, current_user.id, study_id)
        
        if favorite:
            return {"message": "收藏成功"}
        else:
            return ErrorResponse(
                code=400,
                message="已经收藏过该研究"
            )
        
    except Exception as e:
        return ErrorResponse(
            code=500,
            message=f"添加收藏失败: {str(e)}"
        )


@router.delete("/favorites/{study_id}", summary="移除收藏")
async def remove_favorite(
    study_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
) -> Any:
    """
    从收藏中移除研究
    """
    try:
        success = await crud.user_favorite.remove_favorite(db, current_user.id, study_id)
        
        if success:
            return {"message": "移除收藏成功"}
        else:
            return ErrorResponse(
                code=404,
                message="收藏不存在"
            )
        
    except Exception as e:
        return ErrorResponse(
            code=500,
            message=f"移除收藏失败: {str(e)}"
        )


@router.get("/history", response_model=Dict[str, Any], summary="获取浏览历史")
async def get_user_history(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
) -> Any:
    """
    获取用户浏览历史
    """
    try:
        history, total = await crud.user_history.get_user_history(
            db=db,
            user_id=current_user.id,
            page=page,
            size=size
        )
        
        # 获取研究详情
        history_responses = []
        for item in history:
            study = await crud.study.get(db, item.study_id)
            if study:
                history_responses.append(
                    UserHistoryResponse(
                        id=item.id,
                        study_id=study.id,
                        study_title=study.official_title,
                        viewed_at=item.viewed_at
                    )
                )
        
        return {
            "items": history_responses,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
        
    except Exception as e:
        return ErrorResponse(
            code=500,
            message=f"获取浏览历史失败: {str(e)}"
        )


@router.delete("/history", summary="清空浏览历史")
async def clear_history(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
) -> Any:
    """
    清空用户浏览历史
    """
    try:
        count = await crud.user_history.clear_history(db, current_user.id)
        return {"message": f"已清空 {count} 条浏览历史"}
        
    except Exception as e:
        return ErrorResponse(
            code=500,
            message=f"清空浏览历史失败: {str(e)}"
        )


@router.get("/search-history", response_model=List[SearchHistoryResponse], summary="获取搜索历史")
async def get_search_history(
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
) -> Any:
    """
    获取用户搜索历史
    """
    try:
        history = await crud.search_history.get_user_search_history(
            db=db,
            user_id=current_user.id,
            limit=limit
        )
        
        return [
            SearchHistoryResponse(
                id=item.id,
                query=item.query,
                filters=item.filters,
                result_count=item.result_count,
                created_at=item.created_at
            ) for item in history
        ]
        
    except Exception as e:
        return ErrorResponse(
            code=500,
            message=f"获取搜索历史失败: {str(e)}"
        )


@router.post("/feedback", response_model=UserFeedbackResponse, summary="提交用户反馈")
async def create_feedback(
    feedback_in: UserFeedbackCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
) -> Any:
    """
    提交用户反馈
    """
    try:
        # 创建反馈
        feedback = await crud.user_feedback.create(
            db=db,
            obj_in=UserFeedback(
                user_id=current_user.id,
                study_id=feedback_in.study_id,
                feedback_type=feedback_in.feedback_type,
                feedback_text=feedback_in.feedback_text
            )
        )
        
        return UserFeedbackResponse(
            id=feedback.id,
            user_id=feedback.user_id,
            study_id=feedback.study_id,
            feedback_type=feedback.feedback_type,
            feedback_text=feedback.feedback_text,
            status=feedback.status,
            created_at=feedback.created_at,
            updated_at=feedback.updated_at
        )
        
    except Exception as e:
        return ErrorResponse(
            code=500,
            message=f"提交反馈失败: {str(e)}"
        )