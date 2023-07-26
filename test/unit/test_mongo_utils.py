import os

import pytest
import dotenv
import pymongo

from utils.mongo_utils import create_mongo_client, create_db, create_collection, add_user, get_user

dotenv.load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")

TEST_DB = "test_db"
TEST_COLLECTION = "test_collection"


@pytest.fixture(name="mongo_client")
def mongo_db_fixture():
    mongo_client = create_mongo_client(MONGO_URL)
    yield mongo_client
    mongo_client.close()


def test_create_mongo_client(mongo_client):
    assert mongo_client is not None
    assert isinstance(mongo_client, pymongo.MongoClient)


def test_create_db(mongo_client):
    db = create_db(mongo_client, TEST_DB)
    assert db is not None
    assert isinstance(db, pymongo.database.Database)


def test_create_collection(mongo_client):
    db = create_db(mongo_client, TEST_DB)
    collection = create_collection(db, TEST_COLLECTION)
    assert collection is not None
    assert isinstance(collection, pymongo.collection.Collection)


@pytest.mark.parametrize(
    "username, password",
    [
        ("test_user", "test_password"),
        ("test_user2", "test_password2"),
    ],
)
def test_add_user(mongo_client, username, password):
    db = create_db(mongo_client, TEST_DB)
    collection = create_collection(db, TEST_COLLECTION)
    add_user(collection, username, password)
    user = get_user(collection, username)
    assert user is not None
    assert user["username"] == username
    assert user["password"] == password
    db_list = mongo_client.list_database_names()
    assert TEST_DB in db_list
    collection_list = db.list_collection_names()
    assert TEST_COLLECTION in collection_list
