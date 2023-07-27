import os

import pytest
import dotenv
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from utils.mongo_utils import (
    create_mongo_client,
    create_db,
    create_collection,
    add_user,
    get_user,
    delete_user,
)
from utils.constants import TEST_DB, TEST_COLLECTION


dotenv.load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")


TEST_USER_1 = "test_user_1"
TEST_USER_2 = "test_user_2"


@pytest.fixture(name="mongo_client")
def mongo_db_fixture():
    mongo_client = create_mongo_client(MONGO_URL)
    yield mongo_client
    mongo_client.close()


def test_create_mongo_client(mongo_client):
    assert mongo_client is not None
    assert isinstance(mongo_client, MongoClient)


def test_create_db(mongo_client):
    db = create_db(mongo_client, TEST_DB)
    assert db is not None
    assert isinstance(db, Database)


def test_create_collection(mongo_client):
    db = create_db(mongo_client, TEST_DB)
    collection = create_collection(db, TEST_COLLECTION)
    assert collection is not None
    assert isinstance(collection, Collection)


@pytest.mark.parametrize(
    "username, password",
    [
        (TEST_USER_1, "test_password"),
        (TEST_USER_2, "test_password2"),
    ],
)
def test_add_user(mongo_client, username, password):
    db = create_db(mongo_client, TEST_DB)
    collection = create_collection(db, TEST_COLLECTION)
    # adding object to new collection sends to server
    add_user(collection, username, password)
    user = get_user(collection, username)
    assert user is not None
    assert user["username"] == username
    assert user["password"] == password
    db_list = mongo_client.list_database_names()
    assert TEST_DB in db_list
    collection_list = db.list_collection_names()
    assert TEST_COLLECTION in collection_list


@pytest.mark.parametrize(
    "username",
    [
        (TEST_USER_1),
        (TEST_USER_2),
    ],
)
def test_delete_user(mongo_client, username):
    collection = Collection(
        mongo_client[TEST_DB], TEST_COLLECTION
    )
    user = get_user(collection, username)
    assert user is not None
    assert user["username"] == username
    delete_user(collection, username)
    user = get_user(collection, username)
    assert user is None
