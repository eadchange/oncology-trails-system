"""
API v1 路由配置
"""

from fastapi import APIRouter

from app.api.v1.endpoints import studies, users

api_router = APIRouter()

# 临床研究相关路由
api_router.include_router(
    studies.router,
    prefix="/studies",
    tags=["studies"]
)

# 用户相关路由
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)