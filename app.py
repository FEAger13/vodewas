import os
import logging
import asyncio
import threading
from flask import Flask, jsonify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
PORT = int(os.environ.get('PORT', 10000))

logger.info(f"✅ Config loaded: Telegram={bool(TELEGRAM_TOKEN)}, DeepSeek={bool(DEEPSEEK_API_KEY)}")

bot_application = None

if TELEGRAM_TOKEN:
    try:
        from telegram.ext import Application, CommandHandler, MessageHandler, filters
        
        bot_application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        async def start(update, context):
            await update.message.reply_text("🤖 Бот работает! Напишите сообщение.")
        
        async def handle_message(update, context):
            user_message = update.message.text
            response = f"🔮 Вы сказали: {user_message}\n\nБот успешно запущен! 🎉"
            await update.message.reply_text(response)
        
        bot_application.add_handler(CommandHandler("start", start))
        bot_application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        async def run_bot():
            await bot_application.run_polling()
        
        def start_bot():
            asyncio.run(run_bot())
        
        bot_thread = threading.Thread(target=start_bot, daemon=True)
        bot_thread.start()
        logger.info("✅ Telegram bot started successfully!")
        
    except Exception as e:
        logger.error(f"❌ Bot failed: {e}")
else:
    logger.warning("⚠️ TELEGRAM_BOT_TOKEN not set - bot disabled")

@app.route('/')
def home():
    return jsonify({
        "status": "online", 
        "bot_running": bot_application is not None
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=False)
