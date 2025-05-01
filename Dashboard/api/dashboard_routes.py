import os
import uuid
import random
from io import BytesIO
from datetime import datetime
from flask import Blueprint, request, jsonify, session, send_file
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from bson.objectid import ObjectId
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from dotenv import load_dotenv
from scanPlate import process_license_plate

load_dotenv()
mongo_uri     = os.getenv("MONGO_URI")
client        = MongoClient(mongo_uri)
db            = client["smartplate"]
entries       = db["entries"]

# static/uploads folder
BASE_DIR      = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

dashboard_api_bp = Blueprint("dashboard_api", __name__)


@dashboard_api_bp.route("/data", methods=["GET"])
def get_dashboard_data():
    if "username" not in session:
        return jsonify({"status":"fail","message":"Unauthorized"}), 401

    total   = entries.count_documents({})
    entered = entries.count_documents({"status":"entered"})
    exited  = entries.count_documents({"status":"exited"})
    docs    = entries.find({}).sort("entry_time", -1).limit(10)

    recent = []
    for d in docs:
        recent.append({
            "id":           str(d["_id"]),
            "plate_number": d.get("plate_number"),
            "state":        d.get("state"),
            "entry_time":   d.get("entry_time"),
            "exit_time":    d.get("exit_time"),
            "status":       d.get("status"),
            "hours":        d.get("hours", 0),
            "paid_status":  d.get("paid_status", "UNPAID"),
            "fines":        d.get("fines", 0),
            "image_url":    d.get("image_url")
        })

    return jsonify({
        "status":        "success",
        "total_plates":  total,
        "entered_count": entered,
        "exited_count":  exited,
        "recent_activity": recent
    }), 200


@dashboard_api_bp.route("/new-entry", methods=["POST"])
def new_entry():
    if "username" not in session:
        return jsonify({"status":"fail","message":"Unauthorized"}), 401
    if "file" not in request.files:
        return jsonify({"status":"fail","message":"No file uploaded"}), 400

    img      = request.files["file"]
    filename = secure_filename(img.filename)
    tmp_path = os.path.join("/tmp", filename)
    img.save(tmp_path)

    try:
        plate, state, _, data_ts = process_license_plate(tmp_path)
    finally:
        try: os.remove(tmp_path)
        except: pass

    # Resave under static/uploads with a unique name
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    final_path  = os.path.join(UPLOAD_FOLDER, unique_name)
    img.stream.seek(0)
    img.save(final_path)
    image_url = f"/static/uploads/{unique_name}"

    hours       = int(request.form.get("hours", 0) or 0)
    paid_status = request.form.get("paid_status", "UNPAID")

    # Build exactly the JSONable dict
    entry_doc = {
        "plate_number": plate,
        "state":        state,
        "entry_time":   data_ts,
        "exit_time":    None,
        "status":       "entered",
        "hours":        hours,
        "paid_status":  paid_status,
        "fines":        0,
        "image_url":    image_url
    }

    result = entries.insert_one(entry_doc)
    # Now return only pure-Python types
    entry_response = {
        "id":            str(result.inserted_id),
        "plate_number":  plate,
        "state":         state,
        "entry_time":    data_ts,
        "exit_time":     None,
        "status":        "entered",
        "hours":         hours,
        "paid_status":   paid_status,
        "fines":         0,
        "image_url":     image_url
    }

    return jsonify({"status":"success","entry":entry_response}), 200


@dashboard_api_bp.route("/exit-entry/<entry_id>", methods=["POST"])
def exit_entry(entry_id):
    if "username" not in session:
        return jsonify({"status":"fail","message":"Unauthorized"}), 401

    now_ts = datetime.now().strftime("%Y/%m/%d_%H:%M:%S")
    res = entries.update_one(
        {"_id": ObjectId(entry_id), "status":"entered"},
        {"$set": {"exit_time": now_ts, "status": "exited"}}
    )
    if res.matched_count == 0:
        return jsonify({"status":"fail","message":"Entry not found or already exited"}), 400

    d = entries.find_one({"_id": ObjectId(entry_id)})
    return jsonify({
        "status":"success",
        "entry": {
            "id":           str(d["_id"]),
            "plate_number": d["plate_number"],
            "state":        d["state"],
            "entry_time":   d["entry_time"],
            "exit_time":    d["exit_time"],
            "status":       d["status"],
            "hours":        d.get("hours", 0),
            "paid_status":  d.get("paid_status", "UNPAID"),
            "fines":        d.get("fines", 0),
            "image_url":    d.get("image_url")
        }
    }), 200


@dashboard_api_bp.route("/add-fine/<entry_id>", methods=["POST"])
def add_fine(entry_id):
    if "username" not in session:
        return jsonify({"status":"fail","message":"Unauthorized"}), 401

    data = request.get_json() or {}
    try:
        amount = float(data.get("fine", 0))
    except:
        return jsonify({"status":"fail","message":"Invalid fine amount"}), 400

    res = entries.update_one(
        {"_id": ObjectId(entry_id)},
        {"$inc": {"fines": amount}}
    )
    if res.matched_count == 0:
        return jsonify({"status":"fail","message":"Entry not found"}), 404

    d = entries.find_one({"_id": ObjectId(entry_id)})
    return jsonify({
        "status":"success",
        "entry": {"id": str(d["_id"]), "fines": d.get("fines", 0)}
    }), 200


@dashboard_api_bp.route("/delete-entry/<entry_id>", methods=["DELETE"])
def delete_entry(entry_id):
    if "username" not in session:
        return jsonify({"status":"fail","message":"Unauthorized"}), 401
    res = entries.delete_one({"_id": ObjectId(entry_id)})
    if res.deleted_count == 0:
        return jsonify({"status":"fail","message":"Entry not found"}), 404
    return jsonify({"status":"success"}), 200


@dashboard_api_bp.route("/report", methods=["GET"])
def generate_report():
    if "username" not in session:
        return jsonify({"status":"fail","message":"Unauthorized"}), 401

    docs = list(entries.find({}).sort("entry_time", 1))
    buffer = BytesIO()
    p      = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(40, height - 50, "SmartPlate Vehicle Report")

    # Headers
    headers = ["Plate","Entry","Exit","Hours","Paid","Status"]
    xs      = [40, 100, 220, 340, 400, 520]
    p.setFont("Helvetica-Bold", 10)
    y = height - 80
    for i, h in enumerate(headers):
        p.drawString(xs[i], y, h)
    y -= 15

    # Rows
    p.setFont("Helvetica", 9)
    for d in docs:
        if y < 60:
            p.showPage()
            y = height - 50
            p.setFont("Helvetica-Bold", 10)
            for i, h in enumerate(headers):
                p.drawString(xs[i], y, h)
            y -= 15
            p.setFont("Helvetica", 9)

        p.drawString(xs[0], y, str(d.get("plate_number","")))
        p.drawString(xs[1], y, str(d.get("entry_time","")))
        p.drawString(xs[2], y, str(d.get("exit_time","N/A")))
        p.drawString(xs[3], y, str(d.get("hours",0)))
        p.drawString(xs[4], y, str(d.get("paid_status","UNPAID")))
        p.drawString(xs[5], y, str(d.get("status","")))
        y -= 14

    p.save()
    buffer.seek(0)

    suffix   = random.randint(100, 999)
    filename = f"SmartPlateReport{suffix}.pdf"
    return send_file(buffer,
                     as_attachment=True,
                     download_name=filename,
                     mimetype="application/pdf")
