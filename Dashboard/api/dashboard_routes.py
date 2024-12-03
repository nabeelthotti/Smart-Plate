from flask import Blueprint, jsonify
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

# Load MongoDB URI from .env file
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")

# MongoDB Connection
client = MongoClient(mongo_uri)
db = client["smartplate"]
license_plates_collection = db["license_plates"]

# Create blueprint
dashboard_api_bp = Blueprint("dashboard_api", __name__)

@dashboard_api_bp.route("/data", methods=["GET"])
def get_dashboard_data():
    # Fetch data from MongoDB
    total_plates = license_plates_collection.count_documents({})
    active_vehicles = license_plates_collection.count_documents({"status": "entered"})
    recent_activity = list(license_plates_collection.find().sort("entry_time", -1).limit(10))

    # Prepare data for the response
    activity_data = []
    for record in recent_activity:
        activity_data.append({
            "plate_number": record["plate_number"],
            "entry_time": record["entry_time"],
            "exit_time": record.get("exit_time"),
            "status": record["status"]
        })

    # Count entries and exits for the chart
    entered_count = license_plates_collection.count_documents({"status": "entered"})
    exited_count = license_plates_collection.count_documents({"status": "exited"})

    # Return the data
    return jsonify({
        "total_plates": total_plates,
        "active_vehicles": active_vehicles,
        "entered_count": entered_count,
        "exited_count": exited_count,
        "recent_activity": activity_data
    })
