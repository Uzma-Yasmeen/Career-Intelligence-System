# save as test_gemini.py and run: python test_gemini.py
import google.generativeai as genai

# Paste your key directly here just for testing
api_key = "YOUR_GEMINI_API_KEY_HERE"

genai.configure(api_key=api_key)

try:
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content("Say hello in one sentence")
    print("✅ Success:", response.text)
except Exception as e:
    print("❌ Error:", str(e))