from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from models import Todos, Users
from database import Base, SessionLocal, engine
from routers.auth import get_current_user


router = APIRouter(
    prefix="/user",
    tags=["user"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=4)


@router.get("", status_code=status.HTTP_200_OK)
async def get_user(
    user: user_dependency,
    db: db_dependency
):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(Users).filter(Users.id == user["id"]).first()


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    user: user_dependency,
    db: db_dependency,
    user_verification: UserVerification
):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    user_model = db.query(Users).where(Users.id == user.get("id")).first()
    
    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail="Error on password change")
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()
    
    
@router.put("/phone-number/{phone_number}", status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(
    user: user_dependency,
    db: db_dependency,
    phone_number: str
):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    user_model = db.query(Users).where(Users.id == user["id"]).first()
    user_model.phone_number = phone_number
    db.add(user_model)
    db.commit()