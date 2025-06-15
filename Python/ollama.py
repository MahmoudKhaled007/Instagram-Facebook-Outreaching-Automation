from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)


def run_ollama_with_image(prompt, image_path, username):
    """
    Original function preserved exactly as provided
    """
    try:
        # Convert to absolute path (like CMD does)
        abs_image_path = os.path.abspath(image_path)
        destination_dir = "copied_images"
        os.makedirs(destination_dir, exist_ok=True)

        # Verify image exists (like CMD would)
        if not os.path.exists(abs_image_path):
            return f"Error: Image not found at {abs_image_path}"

        # Build the exact command you'd use in CMD
        cmd = ["ollama", "run", "gemma3:12b", f"USER:[img:{abs_image_path}]{prompt}"]

        # Run with same settings as command line
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True,  # Important for Windows path handling
        )

        # Return exact CLI output format
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"Ollama Error: {result.stderr.strip()}"

    except Exception as e:
        return f"Python Error: {str(e)}"


@app.route("/analyze-image", methods=["POST"])
def analyze_image():
    """
    New Flask endpoint that accepts image path in request body
    Preserves all original logic while adding API handling
    """
    try:
        data = request.get_json()

        if not data or "image_path" not in data:
            return jsonify({"error": "Missing image_path in request body"}), 400

        image_path = data["image_path"]
        username = data["username"]
        action = data["action"]

        if action == "message":
            prompt = f"""
SYSTEM INSTRUCTION: You are a comment-generation assistant. You do NOT explain, analyze, describe, or summarize. You only output one friendly Instagram message using the format below and based on the user's visible Instagram photos.

CONTEXT:
- Instagram profile of @{username}
- Visible profile photos show: food (ramen, meals), travel (beaches, landscapes), colorful graphics, beer cans, inspirational quotes, and selfies.

TASK:
Write ONE friendly, short message that could be posted under one of their Instagram posts. It should reference something clearly visible from their profile photos (not necessarily the current post).

STRICT RULES:
1. Message must be 10–15 words.
2. Use the username {username} inside the message.
3. Mention something clearly visible (e.g., ramen, quotes, autumn colors, beer).
4. Add exactly ONE emoji at the end.
5. Do NOT include additional emojis.
6. Output format MUST be exactly:
   message: <{username}, [your message here]>
7. DO NOT write explanations, JSON, summaries, analysis, or headers. Only output the message line.

EXAMPLE OUTPUT:
message: <{username}, That bowl of ramen looked like pure comfort—where was that? 🍜>

Now generate.
"""
        else:  # comment action
            prompt = f"""
SYSTEM INSTRUCTION: You are a social media assistant. You do NOT explain, analyze, describe, or summarize. You ONLY generate one friendly Instagram comment based on the user's profile photos.

CONTEXT:
- Instagram profile of @{username}
- Visible photos include: ramen bowls, beer cans, beach trips, colorful quotes, autumn leaves, casual selfies, and meals.

TASK:
Write ONE short, friendly comment that could go under one of their Instagram posts. It should reference something visible in the profile, not necessarily from the current post.

STRICT RULES:
1. Comment must be 10–15 words.
2. Use the username {username} inside the comment.
3. Mention something clearly visible (e.g., ramen, beach, beer, leaves, quote).
4. Add exactly ONE emoji at the end.
5. Do NOT include additional emojis.
6. Output format MUST be exactly:
   comment: <{username}, [your comment here]>
7. DO NOT include explanations, summaries, JSON, or extra text. Output ONLY the comment line.

EXAMPLE OUTPUT:
comment: <{username}, That beach shot looks like total freedom—love the vibe 🌊>

Now generate.
"""

        output = run_ollama_with_image(prompt, image_path, username).strip()

        # Optional: Enforce expected format (commented for flexibility)
        # if action == "comment":
        #     valid_format = re.match(rf"^comment: <{re.escape(username)}, .{{10,100}}>$", output)
        # else:
        #     valid_format = re.match(rf"^message: <{re.escape(username)}, .{{10,100}}>$", output)
        # if not valid_format:
        #     return jsonify({"error": "Model output did not match expected format", "raw_output": output}), 422

        return jsonify({"message": output})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
