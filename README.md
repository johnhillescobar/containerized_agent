# Agent Containerized Demo

A demo repo for building a **LangChain/LangGraph agent** (unit conversion tools, DTOs, middleware) and **running it in Docker**. Covers agent design with custom state and structured output, plus containerization from Dockerfile to `docker run`. Run locally with `uv` or in a container; includes step-by-step guides for both.

## 📚 Learning Resources

- **👉 [Complete DTO Guide](./docs/DTO_GUIDE.md)** - Why DTOs are critical for agents, step-by-step blueprint, best practices, and architecture patterns.
- **👉 [Containerized Agent Guide](./docs/CONTAINERIZED_AGENT_GUIDE.md)** - Step-by-step guide to building and running the agent in Docker (Dockerfile, build, run, and optional Compose).

This project serves as a practical example implementing all the concepts in the DTO guide and can be run locally or in a container.

## Features

- **Unit Conversion Tools**: Convert between feet/meters and Celsius/Fahrenheit
- **LangGraph State Management**: Custom state tracking for tool calls and conversation metadata
- **Middleware Support**: Logging, retries, summarization, and error handling
- **Structured Output**: Pydantic-based response formatting
- **Context Management**: Automatic summarization and context editing for long conversations

## Project Structure

```
containerized_agent/
├── main.py                 # Main agent orchestration
├── config.py               # LLM and agent configuration
├── pyproject.toml          # Project and dependencies (uv)
├── uv.lock                 # Lockfile for reproducible installs
├── Dockerfile              # Container build for the agent
├── .dockerignore           # Excludes .venv, .env, etc. from build
├── docs/
│   ├── DTO_GUIDE.md        # DTO and agent design guide
│   └── CONTAINERIZED_AGENT_GUIDE.md  # Docker step-by-step
├── dto/
│   └── state.py            # AgentState and AgentResponse models
├── tools/                  # Conversion tools
│   ├── feet_meters.py      # Feet to meters conversion
│   ├── meters_feet.py      # Meters to feet conversion
│   ├── celsius_farenheit.py   # Celsius to Fahrenheit conversion
│   └── fahreheit_celsius.py   # Fahrenheit to Celsius conversion
└── utils/
    └── middlewere_funcs.py # Custom middleware functions
```

## Requirements

- Python >= 3.12
- OpenAI API key (set in `.env` file as `OPENAI_API_KEY`)

## Installation

1. Install dependencies with `uv`:
   ```bash
   uv sync
   ```
   (A `uv.lock` file is included for reproducible installs; the Dockerfile uses it when building the image.)

2. Create a `.env` file in the project root with your OpenAI API key:
   ```env
   OPENAI_API_KEY=your_api_key_here
   ```
   Do not commit `.env`; the Docker image expects secrets via `--env-file` at run time.

## Usage

### Run locally

Install deps and run the agent (ensure `.env` has `OPENAI_API_KEY`):

```bash
uv sync
uv run python main.py
```

Or with an active venv: `python main.py`.

The script runs 10 test questions covering feet/meters and Celsius/Fahrenheit conversions.

### Run in Docker

Build and run the agent in a container (secrets from `.env`, not baked into the image):

```bash
docker build -t containerized_agent .
docker run --rm --env-file .env containerized_agent
```

See [docs/CONTAINERIZED_AGENT_GUIDE.md](./docs/CONTAINERIZED_AGENT_GUIDE.md) for a full walkthrough.

## Architecture

### Agent Flow

1. **State Graph**: Uses LangGraph's `StateGraph` to manage conversation flow
2. **Agent Node**: LangChain agent with structured output via `ToolStrategy`
3. **State Tracking Node**: Custom node that tracks tool calls and updates state
4. **Middleware Chain**: Multiple middleware layers for logging, retries, summarization, and error handling

### State Management

The `AgentState` model tracks:
- Conversation messages
- Tool calls made and count
- Conversion results
- Errors and error flags
- Conversation metadata (turn count, start time)
- Structured responses

### Tools

Each conversion tool:
- Extends `BaseTool` from LangChain
- Uses Pydantic models for input validation
- Returns structured responses with timestamps
- Supports both sync (`_run`) and async (`_arun`) execution

### Middleware

1. **Logging Middleware**: Logs message count before model calls
2. **Tool Retry Middleware**: Retries failed tool calls (max 5 retries)
3. **Summarization Middleware**: Summarizes context when token limit is reached
4. **Context Editing Middleware**: Clears old tool uses to manage context size
5. **Error Handling Middleware**: Catches and formats tool execution errors

## Configuration

Configuration is managed in `config.py`:

- **LLM_CONFIG**: Main agent LLM settings (model, temperature, max_tokens, timeout)
- **LLM_CONFIG_MIDDLEWARE**: Middleware LLM settings (for summarization)
- **AGENT_PROMPT**: System prompt for the agent

Default settings:
- Main model: `gpt-5.2` (temperature: 0.1, max_tokens: 50000)
- Middleware model: `gpt-4.1` (temperature: 0.1, max_tokens: 4000)
- Context summarization trigger: 2000 tokens
- Messages to keep: 4 (after summarization)
- **recursion_limit**: 150 (LangGraph step limit so the agent can finish when the model is non-deterministic; avoids `GraphRecursionError` in container or flaky runs)

## Example Output

```
[Test 1/10]
Question: How many meters are in 185 feet?
------------------------------------------------------------
Answer: 185 feet is equal to 56.388 meters.
Tools used: feet_to_meters
Total tool calls: 1
Structured response: 185 feet is equal to 56.388 meters.
Tool calls in response: ['feet_to_meters']
------------------------------------------------------------
```

## Development

### Adding New Tools

1. Create a new tool file in `tools/` directory
2. Define input/output Pydantic models
3. Extend `BaseTool` and implement `_run` and `_arun` methods
4. Add the tool to the `tools` list in `main.py`

### Modifying State

Update `dto/state.py` to add new state fields. The state is automatically managed by LangGraph's message reducer.

### Customizing Middleware

Add middleware functions in `utils/middlewere_funcs.py` and register them in the `create_agent` call in `main.py`.

## Dependencies

- `langchain`: Core LangChain framework
- `langchain-openai`: OpenAI integration
- `langgraph`: Graph-based agent orchestration
- `pydantic`: Data validation and settings management
- `python-dotenv`: Environment variable management

## License

This is a test/demo project.
