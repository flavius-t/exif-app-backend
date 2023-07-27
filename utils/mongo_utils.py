from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database


USERNAME_FIELD = "username"
PASSWORD_FIELD = "password"


def create_mongo_client(mongo_url: str):
    """
    Creates a MongoClient instance

    Args:
        mongo_url (str): The URL to connect to MongoDB

    Returns:
        MongoClient: connection to MongoDB server instance
    """
    mongo_client = MongoClient(mongo_url)
    return mongo_client


def create_db(mongo_client: MongoClient, db_name: str) -> Database:
    """
    Creates a local MongoDB database object (note this does not create a database on the server)

    Args:
        mongo_client (MongoClient): A MongoClient instance
        db_name (str): The name of the database to create

    Returns:
        Database: A Mongo database
    """
    db = mongo_client[db_name]
    return db


def create_collection(db: Database, collection_name: str) -> Collection:
    """
    Creates a local MongoDB collection (note this does not create a collection on the server)

    Args:
        db (Database): A MongoDB database
        collection_name (str): The name of the collection to create

    Returns:
        Collection: A MongoDB collection
    """
    collection = db[collection_name]
    return collection


def add_user(users: Collection, username: str, password: str) -> None:
    """
    Adds a user to a MongoDB collection

    Args:
        users (Collection): A MongoDB collection
        username (str): The username of the user to add
        password (str): The password of the user to add
    """
    users.insert_one({USERNAME_FIELD: username, PASSWORD_FIELD: password})


def get_user(users: Collection, username: str) -> dict:
    """
    Gets a user from a MongoDB collection

    Args:
        users: A MongoDB collection
        username (str): The username of the user to get

    Returns:
        dict: A MongoDB document
    """
    user = users.find_one({USERNAME_FIELD: username})
    return user


def delete_user(users: dict, username: str) -> None:
    """
    Deletes a user from a MongoDB collection

    Args:
        users: A MongoDB collection
        username (str): The username of the user to delete

    """
    users.delete_one({USERNAME_FIELD: username})
