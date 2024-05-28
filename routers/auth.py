from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal
from models import Users


router = APIRouter()

SECRET_KEY = "e08c6e9f09d4c7f314466559e15e0dce75c80c13cb119f7b882a0f27c1464b27"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    
    
class Token(BaseModel):
    access_token: str
    token_type: str
    
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_user(username: str, password: str, db: Session):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {"sub": username, "id": user_id}
    expires = datetime.now() + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/auth", status_code=status.HTTP_201_CREATED)
async def create_user(
    db: db_dependency,
    create_user_request: CreateUserRequest
):
    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        is_active=True
    )
    
    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)
    return {"user": create_user_model}


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dependency
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return "Failed Authentication"
    token = create_access_token(user.username, user.id, timedelta(minutes=20))
    
    return {"access_token": token, "token_type": "bearer"}