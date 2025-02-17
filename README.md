# 🐍 Deep Research Assistant PY

An AI-powered research tool in Python that helps you explore topics in depth using AI and web search.

## Save 200 dollars a month and use this tool

⭐ A python port with a little more cli pizzazz of [https://github.com/dzhng/deep-research](https://github.com/dzhng/deep-research)

Contribute all you want to this. It was fun tweaking it.

[video demo](https://app.arcade.software/share/e6N8mBQlAMbdc0dmOuS1)

![alt text](./deep-research-py.gif)

## Project Structure

```plaintext
deep_research_py/
├── run.py              # Main CLI interface
├── deep_research.py    # Core research logic
├── feedback.py         # Follow-up question generation
├── prompt.py           # System prompts for AI
└── ai/
    ├── providers.py    # AI service configuration
    └── text_splitter.py # Text processing utilities
```

## Features

- **Interactive Research**: Asks follow-up questions to better understand your needs
- **Depth Control**: Customize research breadth and depth
- **Web Integration**: Uses Firecrawl for reliable web content extraction
- **Smart Synthesis**: Combines multiple sources into coherent findings
- **Beautiful CLI**: Rich text interface with progress tracking
- **Markdown Reports**: Generates well-formatted research reports

## Installation

```bash
uv tool install deep-research-py && cp .env.example .env
```

## Configuration
Open `.env` and replace placeholder values with your actual API keys

### Set up environment variables in .env file:
```bash
# Required by service: "deepseek" and "openai"
# unless you're using DeepSeek or another OpenAI-compliant API.
OPENAI_API_KEY=your-openai-key-here

# Optional: ollama related environment variable
# OLLAMA_API_ENDPOINT=http://localhost:11434

# Required: Firecrawl API key
FIRECRAWL_API_KEY=your-firecrawl-key-here
# If you want to use your self-hosted Firecrawl, add the following below:
# FIRECRAWL_BASE_URL="http://localhost:3002"
```

Note: If you prefer, you can use DeepSeek instead of OpenAI. You can configure it in the `.env` file by setting the relevant API keys and model. Additionally, ensure that you set `DEFAULT_SERVICE` to `"deepseek"` if using DeepSeek or `"openai"` if using OpenAI.

Note: If you want use ollama as your LLM service, set `DEFAULT_SERVICE` to `"ollama"` or use `--service` parameter.

## Usage

Run the research assistant:

```bash
deep-research
```

You'll be prompted to:
1. Enter your research topic
2. Set research breadth (2-10, default 4)
3. Set research depth (1-5, default 2)
4. Answer follow-up questions
5. Wait while it researches and generates a report

You can change the concurrency level by setting the `--concurrency` flag (useful if you have a high API rate limit):

```bash
deep-research --concurrency 10
```

You can get a list of available commands:

```bash
deep-research --help
```

## Development Setup

Clone the repository and set up your environment:

```bash
# Clone the repository
git clone https://github.com/epuerta9/deep-research-py.git
cd deep-research-py

# Create and activate virtual environment
uv venv
source .venv/bin/activate

# Install in development mode
uv pip install -e .

# Copy environment configuration
cp .env.example .env

# Set your API keys by editing the .env file

# Run the tool
deep-research
```

## Requirements

- Python 3.9 or higher
- OpenAI API key (GPT-4 access recommended)
- Firecrawl API key for web search
- Dependencies:
  - openai
  - firecrawl-py
  - typer
  - rich
  - prompt-toolkit
  - aiohttp
  - aiofiles
  - tiktoken

## Output

The tool generates:
- A markdown report saved as `output.md`
- List of sources used
- Summary of key findings
- Detailed analysis of the topic

## License

MIT

## Contributing

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Install development dependencies:
```bash
pip install pre-commit
pre-commit install
```
4. Make your changes
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request
