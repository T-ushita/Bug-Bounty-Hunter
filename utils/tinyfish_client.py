from tinyfish import TinyFish
import os
from dotenv import load_dotenv

load_dotenv()

client = TinyFish(api_key=os.getenv("TINYFISH_API_KEY"))


def search_web(url, goal):

    with client.agent.stream(
        url=url,
        goal=goal,
    ) as stream:

        for event in stream:

            # Only capture final result
            if event.type.value == "COMPLETE":
                return event.result_json

    return {}