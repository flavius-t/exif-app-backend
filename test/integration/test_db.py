import pytest

from utils.mongo_utils import (
    create_db,
    create_collection,
    add_user,
    get_user,
    delete_user,
)
from exif import app, mongo_client, DB_NAME, USERS_COLLECTION


@pytest.fixture(name="client")
def create_app():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

TEST_USER = "test_user"
TEST_PASSWORD = "test_password"

def test_db_connection():
    test_db = create_db(mongo_client, DB_NAME)
    test_collection = create_collection(test_db, USERS_COLLECTION)
    add_user(test_collection, TEST_USER, TEST_PASSWORD)
    db_list = mongo_client.list_database_names()
    assert DB_NAME in db_list
    collection_list = test_db.list_collection_names()
    assert USERS_COLLECTION in collection_list
    user = get_user(test_collection, TEST_USER)
    assert user is not None
    assert user["username"] == TEST_USER
    assert user["password"] == TEST_PASSWORD
    delete_user(test_collection, TEST_USER)
    user = get_user(test_collection, TEST_USER)
    assert user is None
