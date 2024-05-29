from datetime import timedelta

from fastapi import HTTPException
from jose import jwt
from test.utils import *
from routers.auth import ALGORITHM, SECRET_KEY, create_access_token, get_db, authenticate_user, get_current_user


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
    
    
def test_create_access_token():
    username = "testuser"
    user_id = 1
    role = "user"
    expires_delta = timedelta(days=1)
    
    token = create_access_token(username, user_id, role, expires_delta)
    
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM, options={"verify_signature": False})
    
    assert decoded_token["sub"] == username
    assert decoded_token["id"] == user_id
    assert decoded_token["role"] == role
    
    
@pytest.mark.asyncio    
async def test_get_current_user_valid_token():
    
    encode = {"sub": "admin", "id": 1, "role": "admin"}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    
    user = await get_current_user(token=token)
    assert user == {"username": "admin", "id": 1, "user_role": "admin"}
    
    
@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode = {"role": "user"}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token)
        
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Could not validate user."