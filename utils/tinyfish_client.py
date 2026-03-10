import os
import requests
from dotenv import load_dotenv

load_dotenv()

TINYFISH_API_KEY = os.getenv("TINYFISH_API_KEY")

BASE_URL = "https://api.tinyfish.ai/v1/webagent"

def search_web(query: str):
    """
    Calls TinyFish Web Agent API to search the web.
    """

    headers = {
        "Authorization": f"Bearer {TINYFISH_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "query": query,
        "depth": 2
    }

    response = requests.post(
        f"{BASE_URL}/search",
        json=payload,
        headers=headers
    )

    response.raise_for_status()

    return response.json()