import os
import pickle
import pandas as pd
import json
import requests
from tkinter import messagebox, Tk
from playwright.sync_api import sync_playwright

os.environ["PLAYWRIGHT_BROWSERS_PATH"] = r"C:\Users\HP\AppData\Local\ms-playwright"


COOKIE_FILE = "fb_cookies.pkl"

# ---------- COOKIES ----------
def save_cookies(context, cookie_file=COOKIE_FILE):
    cookies = context.cookies()
    with open(cookie_file, "wb") as f:
        pickle.dump(cookies, f)

def load_cookies(context, cookie_file=COOKIE_FILE):
    with open(cookie_file, "rb") as f:
        cookies = pickle.load(f)
    context.add_cookies(cookies)

# ---------- AI CALL ----------
def analyze_image_with_ai(image_url):
    headers = {
        "Authorization": "Bearer sk-or-v1-",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "meta-llama/llama-3.2-11b-vision-instruct:free",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What is in this image? Generate a comment that could be used to interact with this post."},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],                      
            }
        ],
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        data=json.dumps(payload),
    )

    if response.status_code == 200:
        try:
            return response.json()["choices"][0]["message"]["content"]
        except Exception:
            return "No response content received from AI."
    else:
        return f"API Error: {response.status_code}\n{response.text}"

import sys

# ---------- EXCEL FILE INPUT ----------
def get_excel_file_path():
    if len(sys.argv) > 1:
        return sys.argv[1]
    else:
        return "facebook_profiles.xlsx"


# ---------- POPUP ----------
def popup_response(message):
    try:
        root = Tk()
        root.withdraw()
        root.update()
        messagebox.showinfo("AI Response", message)
        root.destroy()
    except Exception as e:
        print(f"[Popup Error] {e}")

# ---------- MAIN FUNCTION ----------
def extract_and_analyze_images(profile_links):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        if os.path.exists(COOKIE_FILE):
            print("✅ Loading saved cookies...")
            load_cookies(context)
            page.goto("https://www.facebook.com", timeout=30000)
            page.wait_for_timeout(5000)
        else:
            print("🔐 No cookies found. Please login manually...")
            page.goto("https://www.facebook.com/login", timeout=30000)
            page.wait_for_timeout(300000)  # Allow time for manual login and captcha
            save_cookies(context)
            print("💾 Cookies saved for future use.")

        for idx, link in enumerate(profile_links):
            try:
                print(f"\n📄 Opening profile {idx+1}: {link}")
                page.goto(link, timeout=60000)
                page.wait_for_timeout(5000)

                image_element = page.query_selector("img[alt^='May be an image of']")

                if image_element:
                    image_url = image_element.get_attribute("src")
                    print(f"🖼️ Found image: {image_url}")

                    ai_result = analyze_image_with_ai(image_url)
                    print("🤖 AI Response:", ai_result)

                    popup_response(f"Profile {idx+1}:\n\n{ai_result}")
                else:
                    print(f"⚠️ No image found in Profile {idx+1}. Skipping...")
                    continue

            except Exception as e:
                print(f"❌ Error on profile {idx+1}: {e}")
                continue

        browser.close()

# ---------- ENTRY ----------
if __name__ == "__main__":
    try:
        excel_path = get_excel_file_path()
        print(f"📄 Loading Excel file: {excel_path}")
        df = pd.read_excel(excel_path)
        profile_urls = df["URL"].dropna().tolist()
        extract_and_analyze_images(profile_urls)
    except Exception as e:
        print(f"❌ Failed to run: {e}")

