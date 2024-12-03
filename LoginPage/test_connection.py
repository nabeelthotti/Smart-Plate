from pymongo import MongoClient

MONGO_URI = "mongodb+srv://nabeel:nhT040702@smart-plate.yripg.mongodb.net/smartplate?retryWrites=true&w=majority"

try:
    client = MongoClient(MONGO_URI)
    db = client["smartplate"]
    print("Connected to MongoDB successfully!")
    print("Collections in database:", db.list_collection_names())
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
