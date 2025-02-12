from flask import Blueprint, jsonify, request, session
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load MongoDB URI from .env file
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")

# MongoDB Connection
client = MongoClient(mongo_uri)
db = client["smartplate"]
users_collection = db["users"]

# Define Blueprint
account_api_bp = Blueprint('account_api', __name__)

# Get Logged-in User Profile
@account_api_bp.route('/user-profile', methods=['GET'])
def get_user_profile():
    if 'username' not in session:
        return jsonify({"status": "fail", "message": "Unauthorized"}), 401

    username = session['username']
    user = users_collection.find_one({"username": username}, {"_id": 0, "password": 0})  # Exclude password
    if not user:
        return jsonify({"status": "fail", "message": "User not found"}), 404

    return jsonify({"status": "success", "user": user}), 200

# Update User Profile
@account_api_bp.route('/update-profile', methods=['PUT'])
def update_user_profile():
    if 'username' not in session:
        return jsonify({"status": "fail", "message": "Unauthorized"}), 401

    current_username = session['username']
    data = request.get_json()

    update_data = {}
    # List of fields that can be updated
    valid_fields = ['name', 'username', 'email', 'phone', 'address', 'password']
    for field in valid_fields:
        if field in data:
            update_data[field] = data[field]

    if not update_data:
        return jsonify({"status": "fail", "message": "No valid fields to update"}), 400

    users_collection.update_one({"username": current_username}, {"$set": update_data})

    # If the username is updated, update the session variable accordingly.
    if 'username' in update_data:
        session['username'] = update_data['username']

    return jsonify({"status": "success", "message": "Profile updated successfully"}), 200
