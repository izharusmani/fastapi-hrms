
import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    raise RuntimeError("MONGODB_URI not set. Create a .env file or set the MONGODB_URI environment variable.")

client = MongoClient(MONGODB_URI)
db = client.hrms_db
