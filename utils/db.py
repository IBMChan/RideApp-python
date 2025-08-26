from pymongo import MongoClient

# MongoDB connection settings
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "ibm-ride-app"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Collections
users_col = db["users"]
rides_col = db["rides"]
vehicles_col = db["vehicles"]
