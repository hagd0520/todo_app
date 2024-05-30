from typing import Annotated
from fastapi import APIRouter, Depends, Form, Request
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates

from database import Base, SessionLocal, engine
from models import Users
from routers.auth import get_current_user


router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not Found"}}
)

Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
        

db_dependency = Annotated[Session, Depends(get_db)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        
class UserVerification(BaseModel):
    username: str
    password: str
    new_password: str
    
    
@router.get("/edit-password", response_class=HTMLResponse)
async def edit_user_view(request: Request):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    
    return templates.TemplateResponse(
        "edit-user-password.html", 
        {"request": request, "user": user}
    )


@router.post("/edit-password", response_class=HTMLResponse)
async def user_password_change(
    request: Request, 
    db: db_dependency,
    username: str = Form(...),
    password: str = Form(...),
    password2: str = Form(...),
):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    
    user_data = db.query(Users).where(Users.username == username).first()
    
    msg = "Invalid username or password"
    
    if user_data:
        if username == user_data.username and bcrypt_context.verify(password, user_data.hashed_password):
            user_data.hashed_password = bcrypt_context.hash(password2)
            db.add(user_data)
            db.commit()
            msg = "Password updated"
            
    return templates.TemplateResponse("edit-user-password.html", {"request": request, "user": user, "msg": msg})



# from typing import Annotated
# from fastapi import APIRouter, Depends, Form, HTTPException, Path, Request
# from passlib.context import CryptContext
# from pydantic import BaseModel, Field
# from sqlalchemy.orm import Session
# from starlette import status
# from starlette.responses import HTMLResponse, RedirectResponse
# from starlette.templating import Jinja2Templates
# from models import Todos, Users
# from database import Base, SessionLocal, engine
# from routers.auth import get_current_user, logout


# router = APIRouter(
#     prefix="/user",
#     tags=["user"]
# )


# templates = Jinja2Templates(directory="templates")


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
        
        
# db_dependency = Annotated[Session, Depends(get_db)]
# user_dependency = Annotated[dict, Depends(get_current_user)]
# bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# class UserVerification(BaseModel):
#     password: str
#     new_password: str = Field(min_length=4)


# @router.get("", status_code=status.HTTP_200_OK)
# async def get_user(
#     user: user_dependency,
#     db: db_dependency
# ):
#     if not user:
#         raise HTTPException(status_code=401, detail="Authentication Failed")
#     return db.query(Users).filter(Users.id == user["id"]).first()


# @router.get("/change-password", response_class=HTMLResponse)
# async def change_password(request: Request):
#     return templates.TemplateResponse("change-password.html", {"request": request})


# @router.post("/change-password", response_class=HTMLResponse)
# async def change_password(
#     request: Request, 
#     db: db_dependency,
#     password: str = Form(...),
#     new_password: str = Form(...),
#     confirm_password: str = Form(...)
# ):
#     user = await get_current_user(request)
#     if not user:
#         return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    
#     user_model = db.query(Users).where(Users.id == user.get("id")).first()
        
#     # 비밀번호 확인
#     if not bcrypt_context.verify(password, user_model.hashed_password):
#         msg = "Incorrect Password"
#         return templates.TemplateResponse("change-password.html", {"request": request, "msg": msg})
    
#     # 새로운 비밀번호가 확인용 비밀번호와 같은지 확인
#     if new_password != confirm_password:
#         msg = "Incorrect Confirm password"
#         return templates.TemplateResponse("change-password.html", {"request": request, "msg": msg})
    
#     user_model.hashed_password = bcrypt_context.hash(new_password)
    
#     db.add(user_model)
#     db.commit()
    
#     msg = "Password changed successfully"
    
#     return await logout(request, msg)
    

# @router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
# async def change_password(
#     user: user_dependency,
#     db: db_dependency,
#     user_verification: UserVerification
# ):
#     if not user:
#         raise HTTPException(status_code=401, detail="Authentication Failed")
#     user_model = db.query(Users).where(Users.id == user.get("id")).first()
    
#     if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
#         raise HTTPException(status_code=401, detail="Error on password change")
#     user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
#     db.add(user_model)
#     db.commit()
    
    
# @router.put("/phone-number/{phone_number}", status_code=status.HTTP_204_NO_CONTENT)
# async def change_phone_number(
#     user: user_dependency,
#     db: db_dependency,
#     phone_number: str
# ):
#     if not user:
#         raise HTTPException(status_code=401, detail="Authentication Failed")
#     user_model = db.query(Users).where(Users.id == user["id"]).first()
#     user_model.phone_number = phone_number
#     db.add(user_model)
#     db.commit()