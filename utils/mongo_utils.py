"""
MongoDB utility functions

Functions:
    create_mongo_client: Creates a MongoClient instance
    create_db: Creates a local MongoDB database object
    create_collection: Creates a local MongoDB collection
    add_user: Adds a user to a MongoDB collection
    get_user: Gets a user from a MongoDB collection
    delete_user: Deletes a user from a MongoDB collection
    close_connection: Closes a MongoClient connection

Exceptions:
    MongoServerConnectionError: If the MongoClient instance fails to connect to the MongoDB server
"""

import logging
import os

from dotenv import load_dotenv

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import ServerSelectionTimeoutError


log = logging.getLogger(__name__)

load_dotenv()

MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

USERNAME_FIELD = "username"
PASSWORD_FIELD = "password"
TIMEOUT_MS = 5000


class MongoServerConnectionError(Exception):
    pass


def create_mongo_client(mongo_url: str) -> MongoClient:
    """
    Creates a MongoClient instance

    Args:
        mongo_url (str): The URL to connect to MongoDB

    Returns:
        MongoClient: connection to MongoDB server instance

    Raises:
        MongoServerConnectionError: If the MongoClient instance fails to connect to the MongoDB server
    """
    log.debug(f"Creating MongoDB client connection to '{mongo_url}'")
    mongo_client = MongoClient(
        mongo_url,
        connectTimeoutMS=TIMEOUT_MS,
        serverSelectionTimeoutMS=TIMEOUT_MS,
        username=MONGO_USER,
        password=MONGO_PASSWORD,
    )
    if not _is_connected_to_server(mongo_client):
        raise MongoServerConnectionError(f"Failed to connect to MongoDB server at '{mongo_url}'")
    return mongo_client


def _is_connected_to_server(mongo_client: MongoClient) -> bool:
    """
    Checks if the MongoClient instance is connected to the MongoDB server

    Args:
        mongo_client (MongoClient): A MongoClient instance

    Returns:
        bool: True if connected, False if not connected
    """
    log.debug(f"Checking MongoDB server connection")
    try:
        mongo_client.admin.command("ismaster")
    except ServerSelectionTimeoutError as e:
        log.error(f"Failed to connect to MongoDB server: {e}")
        return False

    return True


def create_db(mongo_client: MongoClient, db_name: str) -> Database:
    """
    Creates a local MongoDB database object (note this does not create a database on the server)

    Args:
        mongo_client (MongoClient): A MongoClient instance
        db_name (str): The name of the database to create

    Returns:
        Database: A Mongo database
    """
    log.debug(f"Creating database '{db_name}'")
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
    log.debug(f"Creating collection '{collection_name}'")
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
    log.debug(f"Adding user '{username}' to collection '{users.name}'")
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
    log.debug(f"Getting user '{username}' from collection '{users.name}'")
    user = users.find_one({USERNAME_FIELD: username})
    return user


def delete_user(users: dict, username: str) -> None:
    """
    Deletes a user from a MongoDB collection

    Args:
        users: A MongoDB collection
        username (str): The username of the user to delete

    """
    log.debug(f"Deleting user '{username}' from collection '{users.name}'")
    users.delete_one({USERNAME_FIELD: username})


def close_connection(mongo_client: MongoClient) -> None:
    """
    Closes a MongoClient connection

    Args:
        mongo_client (MongoClient): A MongoClient instance
    """
    log.debug(f"Closing MongoDB client connection")
    mongo_client.close()
