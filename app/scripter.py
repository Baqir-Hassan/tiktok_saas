import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the API key from environment variables
api_key = os.getenv("GOOGLE_API_KEY")

# Function to generate script using Gemini 2.5 Flash
def generate_script_with_gemini(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    headers = {
        "Content-Type": "application/json"
    }
    prompt = (
    "Format the following Reddit post into a script for voice narration. "
    "Do not change the wording or add anything new. "
    "Keep the title at the start, followed by the post text. "
    "Output only the formatted narration:\n\n"
    f"{text}"
    )
    body = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    # Send request to Gemini API
    response = requests.post(url, headers=headers, json=body)

    if response.status_code == 200:
        data = response.json()
        try:
            script = data["candidates"][0]["content"]["parts"][0]["text"]
            return script
        except (KeyError, IndexError):
            print("Unexpected response format:", data)
            return None
    else:
        print(f"Error: {response.status_code}")
        print(response.text)  # safer than response.json()
        return None


# Example: Script generation with a Reddit post
if __name__ == "__main__":
    reddit_post = "This is reddit post, make a script from this for a short from tiktock video"
    script = generate_script_with_gemini(reddit_post)
    if script:
        print("Generated Script:")
        print(script)
