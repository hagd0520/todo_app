from starlette import status
from test.utils import *
from routers.users import get_db, get_current_user


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_return_user(test_user):
    response = client.get("/user")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "admin"
    assert response.json()["email"] == "admin@email.com"
    assert response.json()["first_name"] == "ad"
    assert response.json()["last_name"] == "min"
    assert response.json()["role"] == "admin"
    assert response.json()["phone_number"] == "(111)-111-1111"
    