from flask import Blueprint, request, jsonify, session
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")

# MongoDB connection
try:
    client = MongoClient(mongo_uri)
    db = client["smartplate"]
    users_collection = db["users"]
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit(1)

# Create Blueprint
auth_bp = Blueprint("auth_api", __name__)

### **1️⃣ User Signup (Register & Auto-Login)**
@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json() or {}
    name     = data.get("name")
    username = data.get("username")
    email    = data.get("email")
    phone    = data.get("phone")
    pwd      = data.get("password")

    # build address string from the parts (they may be empty)
    street = data.get("street", "").strip()
    city   = data.get("city",  "").strip()
    state  = data.get("state", "").strip()
    zipc   = data.get("zip",   "").strip()
    address = ", ".join(f for f in (street, city, state, zipc) if f)

    # only require the truly mandatory fields
    if not all([name, username, email, phone, pwd]):
        return jsonify({"status": "fail", "message": "Name, username, email, phone and password are required"}), 400

    # now address may be blank, but that’s OK
    if users_collection.find_one({"username": username}):
        return jsonify({"status": "fail", "message": "Username already exists"}), 400

    users_collection.insert_one({
        "name":       name,
        "username":   username,
        "email":      email,
        "phone":      phone,
        "address":    address,       # blank string if user didn’t expand
        "password":   pwd,           # 🔴 still plain-text!
        "created_at": datetime.utcnow()
    })

    session["username"] = username
    return jsonify({"status":"success","message":"User created and logged in successfully"}), 201


### **2️⃣ User Login (Store Session)**
@auth_bp.route("/login", methods=["POST"])
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

    # Store session
    session["username"] = username

    return jsonify({"status": "success", "message": "Login successful"}), 200

### **3️⃣ Get Logged-in User Profile**
@auth_bp.route("/user-profile", methods=["GET"])
def get_user_profile():
    if "username" not in session:
        return jsonify({"status": "fail", "message": "Unauthorized"}), 401

    username = session["username"]
    user = users_collection.find_one({"username": username}, {"_id": 0, "password": 0})  # Exclude password
    if not user:
        return jsonify({"status": "fail", "message": "User not found"}), 404

    return jsonify({"status": "success", "user": user}), 200

### **4️⃣ Update User Profile**
@auth_bp.route("/update-profile", methods=["PUT"])
def update_user_profile():
    if "username" not in session:
        return jsonify({"status": "fail", "message": "Unauthorized"}), 401

    username = session["username"]
    data = request.get_json()

    update_data = {}
    for field in ["name", "email", "phone", "address", "password"]:
        if field in data:
            update_data[field] = data[field]

    if not update_data:
        return jsonify({"status": "fail", "message": "No valid fields to update"}), 400

    users_collection.update_one({"username": username}, {"$set": update_data})

    return jsonify({"status": "success", "message": "Profile updated successfully"}), 200

### **5️⃣ Logout (Clear Session)**
@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"status": "success", "message": "Logged out successfully"}), 200
