# ai_parse.py
import os, json
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def parse_with_openai(text):
    """
    Send a short prompt to OpenAI to parse a property description/title.
    Returns a Python dict or None. If API key not present it returns None.
    """
    if not OPENAI_API_KEY:
        return None
    try:
        import openai
        openai.api_key = OPENAI_API_KEY
        prompt = (
            "Extract short JSON features from this property text. "
            "Return only valid JSON with keys such as 'bedrooms', 'area_sqft', 'type', 'notes'. "
            "If unknown, use null.\n\nText: '''" + text + "'''"
        )
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"user","content":prompt}],
            max_tokens=120,
            temperature=0
        )
        content = resp["choices"][0]["message"]["content"].strip()
        try:
            return json.loads(content)
        except Exception:
            # If not JSON, save raw output
            return {"raw": content}
    except Exception as e:
        print("OpenAI parse error:", e)
        return None
