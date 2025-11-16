from dotenv import load_dotenv
import os
import openai

load_dotenv()
key = os.getenv("OPENAI_API_KEY")
if not key:
    raise SystemExit("OPENAI_API_KEY not set in .env")

openai.api_key = key

# a tiny test call (text completion/chat). This uses low tokens.
resp = openai.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=[{"role":"user","content":"Say hello in one short sentence."}],
    max_tokens=20,
    temperature=0.2
)
print(resp.choices[0].message.content)
