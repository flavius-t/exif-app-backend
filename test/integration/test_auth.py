"""
Integration tests for authentication endpoints.
"""

import pytest
from datetime import timedelta

from flask_jwt_extended import create_access_token, decode_token

from exif import (
    app,
    users,
    REGISTER_SUCCESS,
    LOGIN_SUCCESS,
    ERR_WRONG_PASSWORD,
    ERR_USER_NOT_EXIST,
    LOGOUT_SUCCESS,
)
from utils.mongo_utils import delete_user, add_user
from models.users import USERNAME_FIELD, PASSWORD_FIELD


REGISTER_ENDPOINT = "/register"


@pytest.fixture(name="client")
def create_app():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


TEST_CREDENTIALS = {USERNAME_FIELD: "test_user", PASSWORD_FIELD: "test_password"}


def test_registration_success(client):
    # make sure user doesn't already exist
    delete_user(users, TEST_CREDENTIALS[USERNAME_FIELD])
    response = client.post("/register", json=TEST_CREDENTIALS)
    delete_user(users, TEST_CREDENTIALS[USERNAME_FIELD])

    assert response.status_code == REGISTER_SUCCESS[1]
    data = response.get_json()
    assert data["message"] == REGISTER_SUCCESS[0]


def test_login_success(client):
    client.post("/register", json=TEST_CREDENTIALS)
    response = client.post("/login", json=TEST_CREDENTIALS)
    delete_user(users, TEST_CREDENTIALS[USERNAME_FIELD])
    print(response)

    assert response.status_code == LOGIN_SUCCESS[1]
    data = response.get_json()
    assert data["message"] == LOGIN_SUCCESS[0]
    assert response.headers.get("Set-Cookie") is not None


def test_login_wrong_password(client):
    client.post("/register", json=TEST_CREDENTIALS)
    invalid_login_data = {
        USERNAME_FIELD: TEST_CREDENTIALS[USERNAME_FIELD],
        PASSWORD_FIELD: "wrong_password",
    }
    response = client.post("/login", json=invalid_login_data)
    delete_user(users, TEST_CREDENTIALS[USERNAME_FIELD])

    assert response.status_code == ERR_WRONG_PASSWORD[1]
    data = response.get_json()
    assert data["message"] == ERR_WRONG_PASSWORD[0]
    assert response.headers.get("Set-Cookie") is None


def test_login_user_does_not_exist(client):
    response = client.post("/login", json=TEST_CREDENTIALS)

    assert response.status_code == ERR_USER_NOT_EXIST[1]
    data = response.get_json()
    assert data["message"] == ERR_USER_NOT_EXIST[0]


def test_logout_success(client):
    response = client.post("/register", json=TEST_CREDENTIALS)
    assert response.status_code == REGISTER_SUCCESS[1]
    response = client.post("/login", json=TEST_CREDENTIALS)
    assert response.status_code == LOGIN_SUCCESS[1]

    auth_token = response.headers["Set-Cookie"].split(";")[0].split("=")[1]
    auth_header = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/logout", headers=auth_header)
    delete_user(users, TEST_CREDENTIALS[USERNAME_FIELD])

    assert response.status_code == LOGOUT_SUCCESS[1]
    data = response.get_json()
    assert data["message"] == LOGOUT_SUCCESS[0]
    auth_token = response.headers["Set-Cookie"].split(";")[0].split("=")[1]
    assert auth_token == ""


def test_protected_route_with_auth(client):
    response = client.post("/register", json=TEST_CREDENTIALS)
    assert response.status_code == REGISTER_SUCCESS[1]
    response = client.post("/login", json=TEST_CREDENTIALS)
    assert response.status_code == LOGIN_SUCCESS[1]

    auth_token = response.headers["Set-Cookie"].split(";")[0].split("=")[1]
    auth_header = {"Authorization": f"Bearer {auth_token}"}

    response = client.get("/profile", headers=auth_header)
    delete_user(users, TEST_CREDENTIALS[USERNAME_FIELD])

    assert response.status_code == 200
    assert response.get_json() == {"message": f"Hello, {TEST_CREDENTIALS[USERNAME_FIELD]}!"}


def test_protected_route_no_auth(client):
    auth_header = {"Authorization": "xxxx.yyyy.zzzz"}
    response = client.get("/profile", headers=auth_header)
    assert response.status_code == 401


def test_refresh_expiring_jwts(client):
    with app.test_request_context():
        access_token = create_access_token(
            identity=TEST_CREDENTIALS[USERNAME_FIELD], expires_delta=timedelta(minutes=1)
        )
        expires_target = decode_token(access_token)["exp"]

    auth_header = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/profile", headers=auth_header)

    assert response.status_code == 200
    assert response.headers["Set-Cookie"] is not None

    token = response.headers["Set-Cookie"].split(";")[0].split("=")[1]
    decoded_token = decode_token(token)
    expires_new = decoded_token["exp"]

    assert expires_new > expires_target
