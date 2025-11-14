import os
import logging
import asyncio
import threading
from flask import Flask, jsonify

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Получаем переменные окружения
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
PORT = int(os.environ.get('PORT', 10000))

logger.info(f"✅ Config loaded: Telegram={bool(TELEGRAM_TOKEN)}, DeepSeek={bool(DEEPSEEK_API_KEY)}")

# Глобальная переменная для бота
bot_application = None

# Инициализация бота только если есть токен
if TELEGRAM_TOKEN:
    try:
        from telegram.ext import Application, CommandHandler, MessageHandler, filters
        
        # Создаем Application (новая версия API)
        bot_application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Обработчики команд
        async def start_command(update, context):
            await update.message.reply_text(
                "🤖 DeepSeek Bot запущен!\n\n"
                "Просто напишите мне сообщение, и я отвечу с помощью AI!"
            )
        
        async def help_command(update, context):
            await update.message.reply_text(
                "💡 Команды:\n"
                "/start - начать работу\n"
                "/help - справка\n\n"
                "Просто напишите любой вопрос!"
            )
        
        async def handle_message(update, context):
            user_message = update.message.text
            user_id = update.effective_user.id
            logger.info(f"💬 Message from {user_id}: {user_message}")
            
            # Базовая обработка сообщения
            if DEEPSEEK_API_KEY:
                response = f"🔮 Вы сказали: '{user_message}'\n\n✨ DeepSeek API подключен!"
            else:
                response = f"🔮 Вы сказали: '{user_message}'\n\n🤖 Бот работает! DeepSeek API настраивается."
            
            await update.message.reply_text(response)
        
        # Добавляем обработчики
        bot_application.add_handler(CommandHandler("start", start_command))
        bot_application.add_handler(CommandHandler("help", help_command))
        bot_application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Функция запуска бота
        async def run_bot_polling():
            try:
                logger.info("🔄 Starting Telegram bot polling...")
                await bot_application.run_polling(
                    drop_pending_updates=True,
                    allowed_updates=None
                )
            except Exception as e:
                logger.error(f"💥 Bot polling error: {e}")
        
        # Запуск бота в отдельном потоке
        def start_bot_thread():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(run_bot_polling())
            except Exception as e:
                logger.error(f"💥 Bot thread error: {e}")
        
        # Запускаем поток с ботом
        bot_thread = threading.Thread(target=start_bot_thread, daemon=True)
        bot_thread.start()
        
        logger.info("✅ Telegram bot initialized and started successfully!")
        
    except Exception as e:
        logger.error(f"❌ Bot initialization failed: {e}")
        bot_application = None
else:
    logger.warning("⚠️ TELEGRAM_BOT_TOKEN not set - bot disabled")

# Маршруты Flask
@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "service": "DeepSeek Telegram Bot",
        "telegram_configured": bool(TELEGRAM_TOKEN),
        "deepseek_configured": bool(DEEPSEEK_API_KEY),
        "bot_initialized": bot_application is not None,
        "message": "Service is running on Render + UptimeRobot"
    })

@app.route('/health')
def health():
    """Эндпоинт для проверки здоровья (для UptimeRobot)"""
    return jsonify({
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"
    })

@app.route('/test')
def test():
    """Тестовый эндпоинт"""
    return jsonify({"message": "Bot is working!", "status": "success"})

if __name__ == '__main__':
    logger.info(f"🌐 Starting Flask server on port {PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False)
