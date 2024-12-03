from pymongo import MongoClient
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv
import os

load_dotenv()

mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
    raise ValueError("MONGO_URI is not set in the .env file")

client = MongoClient(mongo_uri)
db = client["smartplate"]

db.license_plates.delete_many({})

# Populate dummy data
plates = ["ABC123", "DEF456", "GHI789", "JKL012", "MNO345"]
statuses = ["entered", "exited"]

for i in range(50):
    plate_number = random.choice(plates)
    entry_time = datetime.utcnow() - timedelta(hours=random.randint(1, 72))
    exit_time = entry_time + timedelta(hours=random.randint(1, 5))
    status = random.choice(statuses)

    db.license_plates.insert_one({
        "plate_number": plate_number,
        "entry_time": entry_time.isoformat(),
        "exit_time": exit_time.isoformat() if status == "exited" else None,
        "status": status,
    })

print("Dummy data inserted into the license_plates collection!")
