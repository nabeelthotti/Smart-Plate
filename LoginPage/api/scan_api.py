from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from scanPlate import process_license_plate  # refactored to not auto-start watcher

scan_bp = Blueprint("scan_api", __name__)

@scan_bp.route("/scan-plate", methods=["POST"])
def scan_plate():
    if "file" not in request.files:
        return jsonify({"status":"fail","message":"No file uploaded"}), 400

    img = request.files["file"]
    filename = secure_filename(img.filename)
    tmp_path = os.path.join("/tmp", filename)
    img.save(tmp_path)

    plate, state, file_ts, data_ts = process_license_plate(tmp_path)
    os.remove(tmp_path)

    return jsonify({
        "status":        "success",
        "plate":         plate,
        "state":         state,
        "fileTimestamp": file_ts,
        "dataTimestamp": data_ts
    }), 200