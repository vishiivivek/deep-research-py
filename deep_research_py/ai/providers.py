import os
import tiktoken
from typing import Optional
from .text_splitter import RecursiveCharacterTextSplitter

# Assuming we're using OpenAI's API
import openai


def create_openai_client(api_key: str, base_url: Optional[str] = None) -> openai.OpenAI:
    return openai.OpenAI(
        api_key=api_key, base_url=base_url or "https://api.openai.com/v1"
    )


# Initialize OpenAI client with better error handling
try:
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_KEY")
    if not api_key:
        raise ValueError(
            "OpenAI API key not found. Please set OPENAI_API_KEY environment variable."
        )

    openai_client = create_openai_client(
        api_key=api_key, base_url=os.environ.get("OPENAI_API_ENDPOINT")
    )
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    raise

MIN_CHUNK_SIZE = 140
encoder = tiktoken.get_encoding(
    "cl100k_base"
)  # Updated to use OpenAI's current encoding


def trim_prompt(
    prompt: str, context_size: int = int(os.environ.get("CONTEXT_SIZE", "128000"))
) -> str:
    """Trims a prompt to fit within the specified context size."""
    if not prompt:
        return ""

    length = len(encoder.encode(prompt))
    if length <= context_size:
        return prompt

    overflow_tokens = length - context_size
    # Estimate characters to remove (3 chars per token on average)
    chunk_size = len(prompt) - overflow_tokens * 3
    if chunk_size < MIN_CHUNK_SIZE:
        return prompt[:MIN_CHUNK_SIZE]

    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=0)

    trimmed_prompt = (
        splitter.split_text(prompt)[0] if splitter.split_text(prompt) else ""
    )

    # Handle edge case where trimmed prompt is same length
    if len(trimmed_prompt) == len(prompt):
        return trim_prompt(prompt[:chunk_size], context_size)

    return trim_prompt(trimmed_prompt, context_size)

