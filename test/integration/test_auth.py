"""
Integration tests for the authentication endpoints.
"""

import pytest
from flask.testing import FlaskClient

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
    add_user(users, TEST_CREDENTIALS[USERNAME_FIELD], TEST_CREDENTIALS[PASSWORD_FIELD])
    response = client.post("/login", json=TEST_CREDENTIALS)
    delete_user(users, TEST_CREDENTIALS[USERNAME_FIELD])

    assert response.status_code == LOGIN_SUCCESS[1]
    data = response.get_json()
    assert data["message"] == LOGIN_SUCCESS[0]
    assert response.headers.get("Set-Cookie") is not None


def test_login_wrong_password(client):
    add_user(users, TEST_CREDENTIALS[USERNAME_FIELD], TEST_CREDENTIALS[PASSWORD_FIELD])
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
