# NanoBot Local AI Agent System

A complete local multi-stage AI agent with:

- Telegram Bot interface
- Fast router (cheap OpenRouter model)
- Planner (Llama 3 8B)
- Executor loop
- Coding model for code/skill generation
- Dynamic skill loading
- Persistent memory
- Telemetry logs
- Learning loop

## Architecture

```text
[ Telegram Bot ]
        ↓
[ FAST ROUTER ]
        ↓
 respond | tool | plan | create_skill | create_agent
                        ↓ (if plan)
               [ THINKING MODEL (planner) ]
                        ↓
               [ EXECUTION ENGINE ]
                        ↓
               [ CODING MODEL (if needed) ]
                        ↓
               [ MEMORY + TELEMETRY + LEARNING LOOP ]
```

## Requirements

- Docker + Docker Compose
- OpenRouter API key
- Telegram Bot token

## Setup

1. Copy env file:

```bash
cp .env.example .env
```

2. Edit `.env` and set:

- `OPENROUTER_API_KEY`
- `TELEGRAM_BOT_TOKEN`

3. Start services:

```bash
docker compose up --build
```

## Telegram Commands

- `/ask <text>`
- `/create_skill <desc>`
- `/create_agent <name>`
- `/memory_save <project> <text>`
- `/memory_load <project>`

## Storage

- Telemetry: `data/logs/telemetry.json`
- Project memory: `memory/projects/<project>/memory.json`
- Learning insights: `memory/global/learning.json`
- Generated skills: `skills/generated_*.py`

## Notes

- Router model defaults to `qwen/qwen2.5-7b-instruct:free`.
- Planner model uses `meta-llama/llama-3-8b-instruct`.
- Coding model uses `mistralai/mistral-7b-instruct`.
- Skill generation validates syntax and restricts writes to `/skills`.
