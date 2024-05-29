from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

import models
from database import Base, engine
from routers import auth, todos, admin, users


app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/healthy")
def health_check():
    return {"status": "Healthy"}

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)