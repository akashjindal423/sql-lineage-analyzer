# gemini_ai.py
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load API Key from .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def generate_explanation(sql_text):
    """Uses Gemini AI to explain the SQL query."""
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")  # Use the latest available version
        response = model.generate_content(f"Explain this SQL query in simple terms:\n\n{sql_text}")
        return response.text
    except Exception as e:
        print(f"❌ Gemini API Error: {e}")
        return "Error: Unable to generate explanation."
