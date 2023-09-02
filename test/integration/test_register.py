"""
Integration tests for the /register endpoint.
"""

import pytest
from flask.testing import FlaskClient

from exif import app, ERR_FIELDS_MISSING, ERR_USER_EXISTS, REGISTER_SUCCESS, ERR_NO_JSON, users
from utils.constants import USERNAME_FIELD, PASSWORD_FIELD
from utils.mongo_utils import delete_user


REGISTER_ENDPOINT = "/register"


@pytest.fixture(name="client")
def create_app():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.mark.parametrize(
    "data, expected",
    [
        ({USERNAME_FIELD: "test_user", PASSWORD_FIELD: "test_password"}, REGISTER_SUCCESS),
        ({USERNAME_FIELD: "test_user", PASSWORD_FIELD: "test_password"}, ERR_USER_EXISTS),
        ({USERNAME_FIELD: "test_user_2"}, ERR_FIELDS_MISSING),
        ({PASSWORD_FIELD: "test_password_2"}, ERR_FIELDS_MISSING),
        ({}, ERR_NO_JSON),
    ],
)
def test_register(client: FlaskClient, data: dict, expected: tuple):
    """
    Test that the register endpoint returns the expected response.

    Args:
        client (FlaskClient): Flask test client
        data (dict): data to post to the endpoint
        expected (tuple): expected response from the endpoint
    """
    # TODO: use test DB instead of production DB, set up which db to use in app config
    response = client.post(REGISTER_ENDPOINT, json=data)
    assert response.status_code == expected[1]
    assert response.data.decode("utf-8") == expected[0]
    if response.status_code == ERR_USER_EXISTS[1]:
        delete_user(users, data[USERNAME_FIELD])
