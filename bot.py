import telegram
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
import threading
import http.server
import socketserver
import os

# Токен бота и ID админа
TOKEN = '7929433274:AAG7SAuW95or_r2kjOc4bLsLvruXzDy-nME'
ADMIN_ID = 5144249911

bot = telegram.Bot(token=TOKEN)

def start(update, context):
    """Обработчик команды /start"""
    update.message.reply_text("Привет! Напиши мне что-нибудь, и я передам это администратору.")

def forward_to_admin(update, context):
    """Пересылает сообщения от пользователей админу"""
    user_message = update.message.text
    user_chat_id = update.message.chat_id
    user_name = update.message.from_user.first_name

    bot.send_message(
        chat_id=ADMIN_ID,
        text=f"Сообщение от {user_name} (ID: {user_chat_id}):\n{user_message}"
    )
    update.message.reply_text("Ваше сообщение отправлено! Ожидайте ответа.")

def reply_to_user(update, context):
    """Обрабатывает ответы админа пользователю"""
    if update.message.chat_id != ADMIN_ID:
        print(f"Сообщение не от админа. Chat ID: {update.message.chat_id}")
        return

    try:
        message_text = update.message.text
        user_chat_id = int(message_text.split()[0])
        reply_text = " ".join(message_text.split()[1:])

        print(f"Попытка отправить сообщение пользователю с ID: {user_chat_id}")
        print(f"Текст ответа: {reply_text}")

        # Отправляем сообщение пользователю
        bot.send_message(chat_id=user_chat_id, text=f"Ответ от админа:\n{reply_text}")
        print(f"Сообщение успешно отправлено пользователю с ID: {user_chat_id}")

        # Отправляем подтверждение админу
        bot.send_message(chat_id=ADMIN_ID, text="Ответ успешно отправлен!")
        print("Подтверждение отправлено админу")
    except (ValueError, IndexError):
        bot.send_message(chat_id=ADMIN_ID, text="Ошибка! Формат: '<chat_id> текст ответа'")
        print("Ошибка: Неверный формат сообщения")
    except Exception as e:
        bot.send_message(chat_id=ADMIN_ID, text=f"Произошла ошибка: {str(e)}")
        print(f"Произошла ошибка: {str(e)}")

def run_bot():
    """Запускает бота"""
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, forward_to_admin))
    dp.add_handler(MessageHandler(Filters.text & Filters.chat(ADMIN_ID), reply_to_user))

    updater.start_polling()
    updater.idle()

def run_server():
    """Запускает простой HTTP-сервер для Render"""
    PORT = int(os.getenv("PORT", 8000))  # Render предоставляет порт через переменную PORT
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving on port {PORT}")
        httpd.serve_forever()

if __name__ == '__main__':
    # Запускаем HTTP-сервер в отдельном потоке
    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    # Запускаем бота
    run_bot()
