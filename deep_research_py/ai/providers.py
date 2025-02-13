import os
import typer
import tiktoken
from typing import Optional
from rich.console import Console
from dotenv import load_dotenv
from .text_splitter import RecursiveCharacterTextSplitter

# Assuming we're using OpenAI's API
import openai

load_dotenv()


def create_openai_client(api_key: str, base_url: Optional[str] = None) -> openai.OpenAI:
    return openai.OpenAI(
        api_key=api_key, base_url=base_url or "https://api.openai.com/v1"
    )


def create_deepseek_client(
    api_key: str, base_url: Optional[str] = None
) -> openai.OpenAI:
    return openai.OpenAI(
        api_key=api_key, base_url=base_url or "https://api.deepseek.com/v1"
    )


# Initialize OpenAI client with better error handling
try:
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY")
    if not api_key:
        raise ValueError(
            "DeepSeek API key not found. Please set OPENAI_API_KEY environment variable."
        )

    openai_client = create_openai_client(
        api_key=api_key, base_url=os.getenv("OPENAI_API_ENDPOINT")
    )
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    raise


def get_ai_client(service: str, console: Console) -> openai.OpenAI:
    # Decide which API key and endpoint to use
    if service.lower() == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        endpoint = os.getenv("OPENAI_API_ENDPOINT", "https://api.openai.com/v1")
        if not api_key:
            console.print("[red]Missing OPENAI_API_KEY in environment[/red]")
            raise typer.Exit(1)
        client = create_openai_client(api_key=api_key, base_url=endpoint)

        return client
    elif service.lower() == "deepseek":
        api_key = os.getenv("DEEPSEEK_API_KEY")
        endpoint = os.getenv("DEEPSEEK_API_ENDPOINT", "https://api.deepseek.com/v1")
        if not api_key:
            console.print("[red]Missing DEEPSEEK_API_KEY in environment[/red]")
            raise typer.Exit(1)
        client = create_deepseek_client(api_key=api_key, base_url=endpoint)

        return client
    else:
        console.print(
            "[red]Invalid service selected. Choose 'openai' or 'deepseek'.[/red]"
        )
        raise typer.Exit(1)


MIN_CHUNK_SIZE = 140
encoder = tiktoken.get_encoding(
    "cl100k_base"
)  # Updated to use OpenAI's current encoding


def trim_prompt(
    prompt: str, context_size: int = int(os.getenv("CONTEXT_SIZE", "128000"))
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
