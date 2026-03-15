from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from models.user import User
from database.session import get_db
from config.settings import settings

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2密码承载令牌方案
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except (ValueError, AttributeError):
        # 如果passlib验证失败，尝试其他方法
        try:
            import bcrypt
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            # 最后尝试sha256
            import hashlib
            return hashlib.sha256(plain_password.encode('utf-8')).hexdigest() == hashed_password


def get_password_hash(password: str) -> str:
    """获取密码哈希值"""
    # bcrypt对密码长度有限制（最多72字节），需要截断长密码
    # 确保UTF-8编码后的字节长度不超过72字节
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        # 截断到72字节，并确保不会在多字节字符中间截断
        truncated_bytes = password_bytes[:72]
        # 尝试解码，如果失败则逐字节减少直到成功
        while True:
            try:
                password = truncated_bytes.decode('utf-8')
                break
            except UnicodeDecodeError:
                if len(truncated_bytes) == 0:
                    password = ""
                    break
                truncated_bytes = truncated_bytes[:-1]
    
    # 使用passlib进行哈希
    try:
        return pwd_context.hash(password)
    except (ValueError, AttributeError) as e:
        # 如果遇到bcrypt相关错误，使用更简单的处理方式
        # 直接使用bcrypt库（如果可用）
        try:
            import bcrypt
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception:
            # 最后手段：使用sha256作为备用方案
            import hashlib
            return hashlib.sha256(password.encode('utf-8')).hexdigest()


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """验证用户"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, str(user.hashed_password)):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception

    if not bool(user.is_active):
        raise HTTPException(status_code=400, detail="Inactive user")

    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """获取当前活跃用户"""
    if not bool(current_user.is_active):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_superuser(current_user: User = Depends(get_current_user)) -> User:
    """获取当前超级用户"""
    if not bool(current_user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user