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


def compress_image(image_path, max_size=768, min_size=512):
    """Compress image to be between min_size and max_size pixels"""
    try:
        with Image.open(image_path) as img:
            # Convert RGBA to RGB if necessary
            if img.mode in ("RGBA", "LA") or (
                img.mode == "P" and "transparency" in img.info
            ):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[3])  # 3 is the alpha channel
                img = background

            # Calculate new dimensions while maintaining aspect ratio
            width, height = img.size
            if width > height:
                new_width = min(max_size, max(min_size, width))
                new_height = int(height * (new_width / width))
            else:
                new_height = min(max_size, max(min_size, height))
                new_width = int(width * (new_height / height))

            # Resize image
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Save to temporary file
            temp_path = f"{image_path}_compressed.jpg"
            resized_img.save(temp_path, "JPEG", quality=85)
            return temp_path
    except Exception as e:
        raise Exception(f"Error compressing image: {str(e)}")


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

    try:
        # Compress the image
        compressed_path = compress_image(file_path)

        # Upload compressed image to ImgBB
        result = upload_to_imgbb(compressed_path)

        # Clean up temporary compressed file
        if os.path.exists(compressed_path):
            os.remove(compressed_path)

        if "error" in result:
            return jsonify({"error": result["error"]}), 500

        return jsonify(result["data"]["image"]["url"])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(host="0.0.0.0", port=5000, debug=True)
