from typing import List
import asyncio
import openai
import json
from .prompt import system_prompt
from .ai.providers import get_client_response


async def generate_feedback(query: str, client: openai.OpenAI, model: str) -> List[str]:
    """Generates follow-up questions to clarify research direction."""

    # Run OpenAI call in thread pool since it's synchronous


    response = await get_client_response(
        client=client,
            model=model,
            messages=[
                {"role": "system", "content": system_prompt()},
                {
                    "role": "user",
                    "content": f"Given this research topic: {query}, generate 3-5 follow-up questions to better understand the user's research needs. Return the response as a JSON object with a 'questions' array field.",
                },
            ],
            response_format={"type": "json_object"},
        )

    # Parse the JSON response
    try:

        return response.get("questions", [])
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        print(f"Raw response: {response}")
        return []
