import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = None
db = None

def get_db():
    """
    Returns the MongoDB database object.
    Initializes the connection if it doesn't exist.
    """
    global client, db
    if db is None:
        try:
            client = MongoClient(MONGO_URI)
            db = client.get_default_database()
            db.command('ping')
            print("MongoDB connection successful.")
        except Exception as e:
            print(f"Could not connect to MongoDB: {e}")
            return None
    return db

def close_db_connection():
    """
    Closes the MongoDB connection if it exists.
    """
    global client
    if client:
        client.close()
        print("MongoDB connection closed.")

def create_document(collection_name, document):
    """Creates a new document in the specified collection."""
    db = get_db()
    if db is None:
        return None, {"error": "Database connection failed"}
    try:
        result = db[collection_name].insert_one(document)
        return result.inserted_id, None
    except Exception as e:
        return None, {"error": str(e)}

def fetch_document(collection_name, query):
    """Fetches a single document from the specified collection based on a query."""
    db = get_db()
    if db is None:
        return None, {"error": "Database connection failed"}
    try:
        document = db[collection_name].find_one(query)
        return document, None
    except Exception as e:
        return None, {"error": str(e)}

def fetch_documents(collection_name, query):
    """Fetches multiple documents from the specified collection based on a query."""
    db = get_db()
    if db is None:
        return None, {"error": "Database connection failed"}
    try:
        documents = list(db[collection_name].find(query))
        return documents, None
    except Exception as e:
        return None, {"error": str(e)}

def update_document(collection_name, query, updates):
    """Updates a single document in the specified collection."""
    db = get_db()
    if db is None:
        return None, {"error": "Database connection failed"}
    try:
        result = db[collection_name].update_one(query, {"$set": updates})
        return result.modified_count, None
    except Exception as e:
        return None, {"error": str(e)}

def delete_document(collection_name, query):
    """Deletes a single document from the specified collection."""
    db = get_db()
    if db is None:
        return None, {"error": "Database connection failed"}
    try:
        result = db[collection_name].delete_one(query)
        return result.deleted_count, None
    except Exception as e:
        return None, {"error": str(e)}
