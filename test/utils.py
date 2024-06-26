import pytest
from sqlalchemy import StaticPool, create_engine, text
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient
from database import Base

from main import app
from models import Todos, Users
from routers.auth import bcrypt_context


DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass= StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
def override_get_current_user():
    return {"username": "test", "id": 1, "user_role": "admin"}


client = TestClient(app)


@pytest.fixture
def test_todo():
    todo = Todos(
        title="Learn to code!",
        description="Need to learn everyday!",
        priority=5,
        complete=False,
        owner_id=1
    )
    
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM todos;"))
        conn.commit()
        
        
@pytest.fixture
def test_user():
    user = Users(
        username="admin",
        email="admin@email.com",
        first_name="ad",
        last_name="min",
        hashed_password=bcrypt_context.hash("1234"),
        role="admin",
        phone_number="(111)-111-1111"
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as conn:
        conn.execute(text("delete from users;"))
        conn.commit()
