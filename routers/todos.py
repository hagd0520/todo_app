from typing import Annotated
from fastapi import APIRouter, Depends, Form, HTTPException, Path, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates
from models import Todos
from database import Base, SessionLocal, engine
from routers.auth import get_current_user


router = APIRouter(
    prefix="/todos",
    tags=["todos"]
)


templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
    
    
@router.get("", response_class=HTMLResponse)
async def read_all_by_user(request: Request, db: db_dependency):
    
    todos = db.query(Todos).filter(Todos.owner_id == 1).all()
    
    return templates.TemplateResponse("home.html", {"request": request, "todos": todos})


@router.get("/add-todo", response_class=HTMLResponse)
async def add_new_todo(request: Request):
    return templates.TemplateResponse("add-todo.html", {"request": request})


@router.post("/add-todo", response_class=HTMLResponse)
async def create_todo(
    request: Request,
    db: db_dependency, 
    title: str = Form(...), 
    description: str = Form(...),
    priority: int = Form(...),
):
    todo_model = Todos()
    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority
    todo_model.complete = False
    todo_model.owner_id = 1
    db.add(todo_model)
    db.commit()
    
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@router.get("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(request: Request, db: db_dependency, todo_id: int):
    
    todo = db.query(Todos).where(Todos.id == todo_id).first()
    
    return templates.TemplateResponse("edit-todo.html", {"request": request, "todo": todo})
    

@router.post("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo_commit(
    request: Request,
    db: db_dependency,
    todo_id: int, 
    title: str = Form(...),
    description: str = Form(...),
    priority: int = Form(...)
):
    todo_model = db.query(Todos).where(Todos.id == todo_id).first()
    
    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority
    
    db.add(todo_model)
    db.commit()
    
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

    
# class TodoRequest(BaseModel):
#     title: str = Field(min_length=3)
#     description: str = Field(min_length=3, max_length=100)
#     priority: int = Field(gt=0, lt=6)
#     complete: bool
    
        
# @router.get("", status_code=status.HTTP_200_OK)
# async def read_all(user: user_dependency, db: db_dependency):
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
#     return db.query(Todos).filter(Todos.owner_id == user["id"]).all()


# @router.get("/{todo_id}", status_code=status.HTTP_200_OK)
# async def read_todo(
#     user: user_dependency,
#     db: db_dependency, 
#     todo_id: int = Path(gt=0)
# ):
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
#     todo_model = db.query(Todos).filter(Todos.id == todo_id) \
#         .filter(Todos.owner_id == user["id"]).first()
#     if todo_model:
#         return todo_model
#     raise HTTPException(status_code=404, detail="Todo not found.")


# @router.post("", status_code=status.HTTP_201_CREATED)
# async def create_todo(
#     user: user_dependency,
#     db: db_dependency, 
#     todo_request: TodoRequest
# ):
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

#     todo_model = Todos(**todo_request.model_dump(), owner_id=user["id"])
    
#     db.add(todo_model)
#     db.commit()
    
    
# @router.put("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def update_todo(
#     user: user_dependency,
#     db: db_dependency, 
#     todo_request: TodoRequest,
#     todo_id: int = Path(gt=0)
# ):
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
#     todo_model = db.query(Todos).filter(Todos.id == todo_id) \
#         .filter(Todos.owner_id == user["id"]).first()
#     if not todo_model:
#         raise HTTPException(status_code=404, detail="Todo not found.")
    
#     todo_model.title = todo_request.title
#     todo_model.description = todo_request.description
#     todo_model.priority = todo_request.priority
#     todo_model.complete = todo_request.complete
    
    
#     db.add(todo_model)
#     db.commit()
    
    
# @router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_todo(
#     user: user_dependency,
#     db: db_dependency, 
#     todo_id: int = Path(gt=0)
# ):
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
#     todo_model = db.query(Todos).filter(Todos.id == todo_id) \
#         .filter(Todos.owner_id == user["id"]).first()
#     if not todo_model:
#         raise HTTPException(status_code=404, detail="Todo not found.")
#     # db.query(Todos).filter(Todos.id == todo_id) \
#     #     .filter(Todos.owner_id == user["id"]).delete()
#     db.delete(todo_model)
    
#     db.commit()