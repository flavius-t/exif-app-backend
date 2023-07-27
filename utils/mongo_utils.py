import pymongo


USERNAME_FIELD = "username"
PASSWORD_FIELD = "password"


def create_mongo_client(mongo_url: str):
    """
    Creates a MongoClient instance

    Args:
        mongo_url (str): The URL to connect to MongoDB

    Returns:
        A MongoClient instance
    """
    mongo_client = pymongo.MongoClient(mongo_url)
    return mongo_client


def create_db(mongo_client: pymongo.MongoClient, db_name: str):
    """
    Creates a database in MongoDB

    Args:
        mongo_client (pymongo.MongoClient): A MongoClient instance
        db_name (str): The name of the database to create

    Returns:
        A MongoDB database
    """
    db = mongo_client[db_name]
    return db


def create_collection(db, collection_name: str):
    """
    Creates a collection in a MongoDB database

    Args:
        db: A MongoDB database
        collection_name (str): The name of the collection to create

    Returns:
        A MongoDB collection
    """
    collection = db[collection_name]
    return collection


def add_user(users, username: str, password: str):
    """
    Adds a user to a MongoDB collection

    Args:
        users: A MongoDB collection
        username (str): The username of the user to add
        password (str): The password of the user to add

    Returns:
        None
    """
    users.insert_one({USERNAME_FIELD: username, PASSWORD_FIELD: password})


def get_user(users, username: str):
    """
    Gets a user from a MongoDB collection

    Args:
        users: A MongoDB collection
        username (str): The username of the user to get

    Returns:
        A MongoDB document
    """
    user = users.find_one({USERNAME_FIELD: username})
    return user


def delete_user(users, username: str):
    """
    Deletes a user from a MongoDB collection

    Args:
        users: A MongoDB collection
        username (str): The username of the user to delete

    Returns:
        None
    """
    users.delete_one({USERNAME_FIELD: username})
