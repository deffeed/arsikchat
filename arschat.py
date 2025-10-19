import os
import logging
import httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# 🔑 Токены из Secrets
TELEGRAM_TOKEN = os.getenv("tgnok")
GROQ_API_KEY = os.getenv("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")

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Функция запроса к Groq Gemini
async def ask_groq(prompt: str) -> str:
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gemma2-9b-it",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Ошибка Groq API: {e}")
        return "⚠️ Ошибка при обращении к ИИ."

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! 🤖 Я ИИ-бот на базе Gemini от Groq.\nНапиши что угодно!")

# Ответ на любое сообщение
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_text("💭 Думаю...")
    reply = await ask_groq(user_text)
    await update.message.reply_text(reply)

# Запуск бота
def main():
    if not TELEGRAM_TOKEN or not GROQ_API_KEY:
        logger.error("❌ Нет TELEGRAM_TOKEN или GROQ_API_KEY в окружении.")
        return

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("✅ Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
