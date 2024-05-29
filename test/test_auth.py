from test.utils import *
from routers.auth import get_db, authenticate_user


app.dependency_overrides[get_db] = override_get_db


def test_authenticate_user(test_user):
    db = TestingSessionLocal()
    
    authenticated_user = authenticate_user(test_user.username, "1234", db)
    assert authenticated_user
    assert authenticated_user.username == test_user.username
    
    non_existent_user = authenticate_user("WrongUserName", "testpassword", db)
    assert not non_existent_user
    
    wrong_password_user = authenticate_user(test_user.username, "wrongpassword", db)
    assert not wrong_password_user