from flask import Flask, request, jsonify
import requests
import os
from werkzeug.utils import secure_filename
from PIL import Image
import io
import base64

app = Flask(__name__)

# Configuration
IMG_BB_API_KEY = "92bd27a7c667852babd0750e6fa3c1b0"  # Replace with your actual key
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_to_imgbb(image_path, expiration=600):
    """Upload image to ImgBB"""
    try:
        with open(image_path, "rb") as file:
            response = requests.post(
                "https://api.imgbb.com/1/upload",
                params={"key": IMG_BB_API_KEY, "expiration": expiration},
                files={"image": file},
            )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


@app.route("/upload", methods=["POST"])
def upload_file():
    # Get JSON data from request
    data = request.get_json()

    if not data or "file_path" not in data:
        return jsonify({"error": "Missing file_path in JSON body"}), 400

    file_path = data["file_path"]

    if not os.path.exists(file_path):
        return jsonify({"error": "File does not exist"}), 400

    if not allowed_file(file_path):
        return jsonify({"error": "File type not allowed"}), 400

    # Upload to ImgBB
    result = upload_to_imgbb(file_path)

    if "error" in result:
        return jsonify({"error": result["error"]}), 500

    return jsonify(result["data"]["image"]["url"])


if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(host="0.0.0.0", port=5000, debug=True)
