from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import User
from app.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user
)
from datetime import timedelta
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


class UserRegister(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int  # 过期时间（小时）


class UserResponse(BaseModel):
    id: str
    username: str
    createdAt: str

    class Config:
        from_attributes = True


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 验证用户名和密码长度
    if len(user_data.username) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名至少需要3个字符"
        )
    if len(user_data.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码至少需要6个字符"
        )
    # bcrypt 限制密码不能超过 72 字节
    password_bytes = user_data.password.encode('utf-8')
    if len(password_bytes) > 72:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码长度不能超过72个字符"
        )
    
    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    user = User(
        username=user_data.username,
        password_hash=hashed_password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user.to_dict()


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """用户登录"""
    # 先检查用户是否存在
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 再检查密码是否正确
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建token
    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.jwt_expire_hours
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user.to_dict()

