from flask import request, jsonify
from pymongo import MongoClient
from datetime import datetime
from . import api_bp

# MongoDB connection
try:
    client = MongoClient("mongodb+srv://nabeel:nhT040702@smart-plate.yripg.mongodb.net/smartplate?retryWrites=true&w=majority")
    db = client["smartplate"]
    users_collection = db["users"]
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit(1)

@api_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    if not data:
        return jsonify({"status": "fail", "message": "Invalid JSON payload"}), 400

    username = data.get("username")
    password = data.get("password")

    # Validate input
    if not username or not password:
        return jsonify({"status": "fail", "message": "Username and password are required"}), 400

    # Check if username already exists
    if users_collection.find_one({"username": username}):
        return jsonify({"status": "fail", "message": "Username already exists"}), 400

    # Store plain text password
    users_collection.insert_one({
        "username": username,
        "password": password,  # Store plain text password
        "created_at": datetime.utcnow(),
    })

    return jsonify({"status": "success", "message": "User created successfully"}), 201

@api_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"status": "fail", "message": "Invalid JSON payload"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"status": "fail", "message": "Username and password are required"}), 400

    user = users_collection.find_one({"username": username, "password": password})
    if not user:
        return jsonify({"status": "fail", "message": "Invalid credentials"}), 401

    return jsonify({"status": "success", "message": "Login successful"}), 200
