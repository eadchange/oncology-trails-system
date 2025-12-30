"""
安全相关工具函数
"""

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建访问令牌
    
    Args:
        data: 要编码的数据
        expires_delta: 过期时间增量
        
    Returns:
        JWT令牌字符串
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    验证JWT令牌
    
    Args:
        token: JWT令牌
        
    Returns:
        解码后的数据或None
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def get_password_hash(password: str) -> str:
    """
    获取密码哈希
    
    Args:
        password: 明文密码
        
    Returns:
        密码哈希
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 密码哈希
        
    Returns:
        是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def generate_password_reset_token(email: str) -> str:
    """
    生成密码重置令牌
    
    Args:
        email: 用户邮箱
        
    Returns:
        重置令牌
    """
    delta = timedelta(hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    验证密码重置令牌
    
    Args:
        token: 重置令牌
        
    Returns:
        邮箱地址或None
    """
    try:
        decoded_token = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )
        return decoded_token["sub"]
    except JWTError:
        return None


def generate_email_verification_token(email: str) -> str:
    """
    生成邮箱验证令牌
    
    Args:
        email: 用户邮箱
        
    Returns:
        验证令牌
    """
    delta = timedelta(hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    return encoded_jwt


def verify_email_verification_token(token: str) -> Optional[str]:
    """
    验证邮箱验证令牌
    
    Args:
        token: 验证令牌
        
    Returns:
        邮箱地址或None
    """
    try:
        decoded_token = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )
        return decoded_token["sub"]
    except JWTError:
        return None


def validate_password(password: str) -> bool:
    """
    验证密码强度
    
    Args:
        password: 密码
        
    Returns:
        是否有效
    """
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        return False
    
    # 检查是否包含数字
    if not any(c.isdigit() for c in password):
        return False
    
    # 检查是否包含字母
    if not any(c.isalpha() for c in password):
        return False
    
    return True