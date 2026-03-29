import os
from typing import Optional

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from core.agent import AgentCore
from core.memory import load_memory, save_memory

AGENT = AgentCore(project="telegram")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")


def _require_text(args: list[str], fallback: str = "") -> str:
    return " ".join(args).strip() or fallback


async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    prompt = _require_text(context.args)
    if not prompt:
        await update.message.reply_text("Usage: /ask <text>")
        return
    result = AGENT.process_input(prompt)
    await update.message.reply_text(result[:4000])


async def create_skill_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    desc = _require_text(context.args)
    if not desc:
        await update.message.reply_text("Usage: /create_skill <description>")
        return
    result = AGENT.process_input(f"create a new skill: {desc}")
    await update.message.reply_text(result[:4000])


async def create_agent_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    name = _require_text(context.args)
    if not name:
        await update.message.reply_text("Usage: /create_agent <name>")
        return
    result = AGENT.process_input(f"create agent named {name}")
    await update.message.reply_text(result[:4000])


async def memory_save_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /memory_save <project> <text>")
        return
    project = context.args[0]
    text = " ".join(context.args[1:])
    save_memory(project, "telegram_note", text)
    await update.message.reply_text("Memory saved")


async def memory_load_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    project: Optional[str] = context.args[0] if context.args else "telegram"
    memory = load_memory(project)
    await update.message.reply_text(str(memory)[:4000])


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("NanoBot agent is running. Use /ask to begin.")


def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("ask", ask_command))
    app.add_handler(CommandHandler("create_skill", create_skill_command))
    app.add_handler(CommandHandler("create_agent", create_agent_command))
    app.add_handler(CommandHandler("memory_save", memory_save_command))
    app.add_handler(CommandHandler("memory_load", memory_load_command))
    app.run_polling()


if __name__ == "__main__":
    main()
