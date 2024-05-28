from fastapi import FastAPI

import models
from database import Base, engine
from routers import auth, todos, admin


app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)