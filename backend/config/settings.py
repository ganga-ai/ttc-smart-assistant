import os
from openai import OpenAI
from dotenv import load_dotenv

# Loading API key from secret.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
dotenv_path = os.path.join(BASE_DIR, ".secrets")
load_dotenv(dotenv_path, override=True)
API_KEY = os.getenv("OPENAI_API_KEY")

# Creating an OpenAI client.
client_openai = OpenAI(
    base_url = "https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1",
    api_key = os.getenv("OPENAI_API_KEY"),
    default_headers = {"x-api-key": os.getenv("API_GATEWAY_KEY")}
)

try:
    response = client_openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "hello"}]
    )
    print(response.choices[0].message.content)

except Exception as e:
    print("TEST ERROR:", e)

# print("DOTENV PATH:", dotenv_path)
# print("EXISTS:", os.path.exists(dotenv_path))

# print("OPENAI:", os.getenv("OPENAI_API_KEY"))
# print("GATEWAY:", os.getenv("API_GATEWAY_KEY"))