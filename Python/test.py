# from flask import Flask, request, jsonify, Response
# from langchain_community.llms import Ollama
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.runnables import RunnablePassthrough
# import os
# import re
# import time
# import json
# from concurrent.futures import ThreadPoolExecutor
# from functools import lru_cache
# import threading
# from queue import Queue
# import hashlib

# app = Flask(__name__)

# # Initialize Ollama with better settings for complete generation
# llm = Ollama(
#     model="gemma3:12b",
#     temperature=0.7,  # Increased for more creative but controlled output
#     base_url="http://localhost:11434",
#     top_p=0.9,  # Increased for better variety
#     num_ctx=4096,  # Reduced for faster processing
#     num_predict=256,  # Increased to ensure full comment generation
#     repeat_penalty=1.05,  # Slightly reduced
#     stop=["```", "---", "###"]  # Better stop tokens for Gemma
# )

# # Thread pool for parallel processing
# executor = ThreadPoolExecutor(max_workers=3)

# # Response cache with TTL
# class CacheEntry:
#     def __init__(self, value, timestamp):
#         self.value = value
#         self.timestamp = timestamp

# response_cache = {}
# cache_lock = threading.Lock()
# CACHE_TTL = 3600  # 1 hour

# # OPTIMIZED PROMPTS FOR GEMMA
# post_analysis_prompt = """Analyze this Instagram post screenshot and extract details.

# Image path: {image_path}

# Extract these details:
# - USERNAME: The exact @handle of the post owner
# - POST_TYPE: Type of post (selfie, gaming setup, lifestyle, etc)
# - VISUALS: List 3-4 specific visual elements
# - VIBE: Overall mood/style

# Respond in this exact format:
# USERNAME: [username without @]
# POST_TYPE: [type]
# VISUALS: [element1, element2, element3]
# VIBE: [description]"""

# comment_generation_prompt = """Generate a two-paragraph Instagram comment for a streamer based on this analysis:

# {analysis}

# Requirements:
# 1. First paragraph (20-25 words): Personal compliment about specific visual element + engaging question
# 2. Second paragraph (25-30 words): Must include these exact phrases:
#    - "I've been working on elevating streamers' branding"
#    - "recently designed for [choose 2 from: Drdisrespect, DOOM49, Nitro Luke DX, OvertimeAU]"
#    - "and some of our mutual friends"
#    - "I thought a comment would be more respectful than a DM"
#    - "I'd love to share the ideas I have in mind for transforming your channel - interested?"

# Example format:
# "[Compliment about specific detail], [name]! [Observation]. [Question about detail] - [follow-up]?

# I've been working on elevating streamers' branding, recently designed for [streamer1], [streamer2], and some of our mutual friends. I thought a comment would be more respectful than a DM. I'd love to share the ideas I have in mind for transforming your channel - interested?"

# Generate the comment now:"""

# # Enhanced username extraction
# def extract_username_from_analysis(analysis):
#     """Extract and clean username from analysis"""
#     try:
#         for line in analysis.split('\n'):
#             if 'USERNAME:' in line:
#                 username = line.split(':', 1)[1].strip()
#                 # Clean common patterns
#                 username = username.replace('@', '').replace('_', ' ')
#                 username = username.split()[0] if username else "friend"
#                 return username.capitalize()
#         return "friend"
#     except:
#         return "friend"

# # Enhanced visual extraction
# def extract_visuals_from_analysis(analysis):
#     """Extract visual elements with better parsing"""
#     try:
#         for line in analysis.split('\n'):
#             if 'VISUALS:' in line:
#                 visuals = line.split(':', 1)[1].strip()
#                 # Get first visual element for natural language
#                 elements = [v.strip() for v in visuals.split(',')]
#                 return elements[0] if elements else "great style"
#         return "awesome setup"
#     except:
#         return "great content"

# # Generate cache key
# def get_cache_key(image_path):
#     """Generate cache key based on file path and modification time"""
#     try:
#         mtime = os.path.getmtime(image_path)
#         key_string = f"{image_path}_{mtime}"
#         return hashlib.md5(key_string.encode()).hexdigest()
#     except:
#         return None

# # Clean expired cache entries
# def clean_cache():
#     """Remove expired cache entries"""
#     current_time = time.time()
#     with cache_lock:
#         expired_keys = [
#             key for key, entry in response_cache.items()
#             if current_time - entry.timestamp > CACHE_TTL
#         ]
#         for key in expired_keys:
#             del response_cache[key]

# # Fast analysis with improved caching
# @lru_cache(maxsize=100)
# def fast_analysis(image_path):
#     """Optimized analysis with LRU caching"""
#     analysis_prompt = ChatPromptTemplate.from_template(post_analysis_prompt)
#     analysis_chain = analysis_prompt | llm

#     start_time = time.time()

#     try:
#         # Invoke with timeout
#         analysis_result = analysis_chain.invoke(
#             {"image_path": image_path},
#             config={"timeout": 10.0}
#         )

#         # Clean and validate result
#         analysis = analysis_result.strip()

#         # Validate structure
#         required_fields = ['USERNAME:', 'POST_TYPE:', 'VISUALS:', 'VIBE:']
#         if all(field in analysis for field in required_fields):
#             print(f"✓ Analysis completed in {time.time() - start_time:.2f}s")
#             return analysis
#         else:
#             print("⚠ Analysis missing fields, using defaults")
#             return generate_default_analysis()

#     except Exception as e:
#         print(f"✗ Analysis error: {e}")
#         return generate_default_analysis()

# def generate_default_analysis():
#     """Generate default analysis as fallback"""
#     return """USERNAME: creator
# POST_TYPE: content post
# VISUALS: professional setup, quality lighting, engaging background
# VIBE: creative and authentic"""

# # Improved comment generation
# def generate_comment_with_retry(analysis, max_retries=2):
#     """Generate comment with retry logic"""
#     comment_prompt = ChatPromptTemplate.from_template(comment_generation_prompt)
#     comment_chain = comment_prompt | llm

#     streamers_pool = [
#         ["Drdisrespect", "DOOM49"],
#         ["Nitro Luke DX", "OvertimeAU"],
#         ["Drdisrespect", "OvertimeAU"],
#         ["DOOM49", "Nitro Luke DX"]
#     ]

#     for attempt in range(max_retries):
#         start_time = time.time()

#         try:
#             # Generate comment
#             result = comment_chain.invoke(
#                 {"analysis": analysis},
#                 config={"timeout": 15.0}
#             )

#             comment = result.strip()

#             # Clean up any remaining formatting
#             comment = re.sub(r'\[INST\]|\[/INST\]|```|###', '', comment).strip()

#             # Validate structure
#             paragraphs = [p.strip() for p in comment.split('\n') if p.strip()]

#             if len(paragraphs) >= 2:
#                 # Ensure proper formatting
#                 final_comment = f"{paragraphs[0]}\n\n{paragraphs[1]}"

#                 # Validate content
#                 if validate_comment_content(final_comment):
#                     print(f"✓ Comment generated in {time.time() - start_time:.2f}s")
#                     return final_comment

#             print(f"⚠ Attempt {attempt + 1} failed validation, retrying...")

#         except Exception as e:
#             print(f"✗ Generation error on attempt {attempt + 1}: {e}")

#     # Fallback generation
#     return create_fallback_comment(analysis, streamers_pool[0])

# def validate_comment_content(comment):
#     """Validate comment has required elements"""
#     lower_comment = comment.lower()
#     required_phrases = [
#         "elevating streamers",
#         "designed for",
#         "mutual friends",
#         "respectful than a dm",
#         "transforming your channel"
#     ]

#     # Check at least 3 required phrases
#     matches = sum(1 for phrase in required_phrases if phrase in lower_comment)
#     return matches >= 3

# def create_fallback_comment(analysis, streamers):
#     """Create high-quality fallback comment"""
#     username = extract_username_from_analysis(analysis)
#     visual = extract_visuals_from_analysis(analysis)

#     # Get post type for better personalization
#     post_type = "content"
#     for line in analysis.split('\n'):
#         if 'POST_TYPE:' in line:
#             post_type = line.split(':', 1)[1].strip().lower()
#             break

#     # Craft personalized first paragraph based on post type
#     if "selfie" in post_type:
#         para1 = f"Clean shot, {username}! Really digging the {visual} aesthetic you've got. How long have you been creating content - what's your main focus?"
#     elif "gaming" in post_type:
#         para1 = f"Sick setup, {username}! That {visual} is looking clean. What games are you mainly streaming these days - variety or focused?"
#     else:
#         para1 = f"Great content, {username}! Love the {visual} vibe you're putting out. What inspired you to start creating - been at it long?"

#     para2 = f"I've been working on elevating streamers' branding, recently designed for {streamers[0]}, {streamers[1]}, and some of our mutual friends. I thought a comment would be more respectful than a DM. I'd love to share the ideas I have in mind for transforming your channel - interested?"

#     return f"{para1}\n\n{para2}"

# # Async wrapper for better performance
# def process_request_async(image_path):
#     """Process request in thread pool"""
#     future = executor.submit(process_image, image_path)
#     return future

# def process_image(image_path):
#     """Main processing logic"""
#     # Check cache first
#     cache_key = get_cache_key(image_path)
#     if cache_key:
#         with cache_lock:
#             if cache_key in response_cache:
#                 entry = response_cache[cache_key]
#                 if time.time() - entry.timestamp < CACHE_TTL:
#                     print("✓ Returning cached response")
#                     return entry.value

#     # Analyze image
#     analysis = fast_analysis(image_path)

#     # Generate comment
#     comment = generate_comment_with_retry(analysis)

#     # Prepare response
#     result = {
#         "comment": comment,
#         "analysis": analysis,
#         "word_count": len(comment.split()),
#         "username": extract_username_from_analysis(analysis)
#     }

#     # Cache result
#     if cache_key:
#         with cache_lock:
#             response_cache[cache_key] = CacheEntry(result, time.time())
#             # Clean old entries periodically
#             if len(response_cache) > 100:
#                 clean_cache()

#     return result

# @app.route("/generate", methods=["POST"])
# def generate():
#     """Main generation endpoint with streaming support"""
#     start_time = time.time()

#     try:
#         data = request.get_json()
#         image_path = data.get("image_path")
#         stream = data.get("stream", False)

#         if not image_path:
#             return jsonify({"error": "image_path is required"}), 400

#         # Verify image exists
#         abs_path = os.path.abspath(image_path)
#         if not os.path.exists(abs_path):
#             return jsonify({"error": f"Image not found at {abs_path}"}), 404

#         print(f"\n🎯 Processing: {os.path.basename(abs_path)}")

#         # Process request
#         result = process_image(abs_path)

#         # Format response
#         response_data = {
#             "response": result["comment"],
#             "word_count": result["word_count"],
#             "target_range": "45-55 words",
#             "analysis": result["analysis"],
#             "generation_time": f"{time.time() - start_time:.2f}s",
#             "metadata": {
#                 "model": "gemma3:12b",
#                 "username_extracted": result["username"],
#                 "cached": False,
#                 "optimizations": [
#                     "LRU caching",
#                     "Retry logic",
#                     "Fallback generation",
#                     "Thread pooling"
#                 ]
#             }
#         }

#         if stream:
#             # Return as server-sent events
#             def generate():
#                 yield f"data: {json.dumps(response_data)}\n\n"

#             return Response(generate(), mimetype="text/event-stream")
#         else:
#             return jsonify(response_data)

#     except Exception as e:
#         print(f"✗ Request error: {str(e)}")
#         return jsonify({
#             "error": str(e),
#             "generation_time": f"{time.time() - start_time:.2f}s"
#         }), 500

# @app.route("/batch", methods=["POST"])
# def batch_generate():
#     """Process multiple images in parallel"""
#     start_time = time.time()

#     try:
#         data = request.get_json()
#         image_paths = data.get("image_paths", [])

#         if not image_paths:
#             return jsonify({"error": "image_paths array is required"}), 400

#         # Process in parallel
#         futures = []
#         for path in image_paths[:10]:  # Limit to 10 for safety
#             abs_path = os.path.abspath(path)
#             if os.path.exists(abs_path):
#                 futures.append(executor.submit(process_image, abs_path))

#         # Collect results
#         results = []
#         for i, future in enumerate(futures):
#             try:
#                 result = future.result(timeout=30)
#                 results.append({
#                     "image": image_paths[i],
#                     "comment": result["comment"],
#                     "word_count": result["word_count"]
#                 })
#             except Exception as e:
#                 results.append({
#                     "image": image_paths[i],
#                     "error": str(e)
#                 })

#         return jsonify({
#             "results": results,
#             "total_time": f"{time.time() - start_time:.2f}s",
#             "processed": len(results)
#         })

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.route("/health", methods=["GET"])
# def health_check():
#     """Enhanced health check with diagnostics"""
#     try:
#         start_time = time.time()

#         # Test model
#         test_response = llm.invoke("Hi", config={"timeout": 5.0})
#         model_time = time.time() - start_time

#         # Cache stats
#         with cache_lock:
#             cache_size = len(response_cache)
#             clean_cache()
#             cache_size_after = len(response_cache)

#         return jsonify({
#             "status": "healthy",
#             "model": {
#                 "name": "gemma3:12b",
#                 "connected": True,
#                 "response_time": f"{model_time:.2f}s"
#             },
#             "cache": {
#                 "entries": cache_size,
#                 "cleaned": cache_size - cache_size_after,
#                 "ttl_seconds": CACHE_TTL
#             },
#             "performance": {
#                 "thread_pool_size": executor._max_workers,
#                 "optimizations": [
#                     "Response caching with TTL",
#                     "LRU analysis cache",
#                     "Thread pool execution",
#                     "Retry logic",
#                     "Batch processing",
#                     "Streaming support"
#                 ]
#             }
#         })

#     except Exception as e:
#         return jsonify({
#             "status": "unhealthy",
#             "error": str(e)
#         }), 503

# @app.route("/clear-cache", methods=["POST"])
# def clear_cache_endpoint():
#     """Clear all caches"""
#     # Clear response cache
#     with cache_lock:
#         response_cache_size = len(response_cache)
#         response_cache.clear()

#     # Clear LRU cache
#     fast_analysis.cache_clear()

#     return jsonify({
#         "message": "All caches cleared",
#         "cleared": {
#             "response_cache": response_cache_size,
#             "analysis_cache": "cleared"
#         }
#     })

# if __name__ == "__main__":
#     print("\n🚀 Optimized Streamer Engagement Comment Generator v2.0")
#     print("=" * 60)

#     print("\n📊 Configuration:")
#     print(f"  • Model: gemma3:12b")
#     print(f"  • Temperature: 0.7 (balanced creativity)")
#     print(f"  • Max tokens: 256 (full comments)")
#     print(f"  • Thread pool: {executor._max_workers} workers")
#     print(f"  • Cache TTL: {CACHE_TTL}s")

#     print("\n🔧 Optimizations:")
#     print("  ✓ Multi-level caching (Response + LRU)")
#     print("  ✓ Parallel batch processing")
#     print("  ✓ Retry logic with fallbacks")
#     print("  ✓ Streaming response support")
#     print("  ✓ Automatic cache cleanup")
#     print("  ✓ Thread pool execution")

#     print("\n🌐 Endpoints:")
#     print("  POST /generate - Generate single comment")
#     print("  POST /batch - Process multiple images")
#     print("  POST /clear-cache - Clear all caches")
#     print("  GET /health - System diagnostics")

#     print("\n📝 Example Request:")
#     print('  curl -X POST http://localhost:5000/generate \\')
#     print('    -H "Content-Type: application/json" \\')
#     print('    -d \'{"image_path": "path/to/image.jpg"}\'')

#     print("\n✨ Starting server...\n")

#     app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
from flask import Flask, request, jsonify
import base64
import requests
import os

app = Flask(__name__)


# Function to convert image to Base64
def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


@app.route("/generate", methods=["POST"])
def analyze_image():
    # Get image path and username from the request
    # image_path = request.form.get("image_path", "").strip()

    # username = request.form.get("username")

    # if not image_path or not os.path.exists(image_path):
    #     return jsonify({"error": "Invalid or missing image path"}), 400

    # if not username:
    #     return jsonify({"error": "Username is required"}), 400

    # Convert image to Base64
    image_base64 = request.form.get("image_base64")

    # Define the payload for the POST request
    payload = {
        "model": "gemma3:12b",
        "prompt": "describe the image. this is instagram post, what should i comment on this post, lmk after analyzing in 100 words ,just send me the comment only",
        "stream": False,
        "images": [image_base64],
    }

    try:
        # Send POST request

        response = requests.post("http://localhost:11434/api/generate", json=payload)
        response.raise_for_status()
        result = response.json()
        return jsonify(
            {
                # "username": username,
                "comment": result.get("response", "No response from model"),
            }
        )

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
