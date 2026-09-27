
import os
import json
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)
load_dotenv()
TOKEN=os.getenv("TOKEN")

# Состояния диалога
NAME, COLOR = range(2)

# Данные пользователей
user_data = {}


def load_data():
    """Загрузка профилей из JSON-файла."""
    global user_data

    if os.path.exists("user.json"):
        with open("user.json", "r", encoding="utf-8") as f:
            user_data = json.load(f)


def save_data():
    """Сохранение профилей в JSON-файл."""
    with open("user.json", "w", encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False, indent=4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало создания профиля."""
    await update.message.reply_text("Привет! Как тебя зовут?")
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение имени пользователя."""
    context.user_data["name"] = update.message.text

    await update.message.reply_text("Какой твой любимый цвет?")
    return COLOR


async def get_color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение цвета и сохранение профиля."""
    user_id = str(update.effective_user.id)

    # Получаем цвет из сообщения
    color = update.message.text

    # Сохраняем профиль в общий словарь по user_id
    user_data[user_id] = {
        "name": context.user_data["name"],
        "color": color,
    }

    # Записываем изменения в JSON-файл
    save_data()

    await update.message.reply_text(
        f"Профиль сохранён!\n"
        f"Имя: {context.user_data['name']}\n"
        f"Цвет: {color}"
    )

    return ConversationHandler.END


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает сохранённый профиль пользователя."""
    user_id = str(update.effective_user.id)

    if user_id not in user_data:
        await update.message.reply_text(
            "Профиль пока не создан. Используй /start."
        )
        return

    profile_data = user_data[user_id]

    await update.message.reply_text(
        f"Твой профиль:\n"
        f"Имя: {profile_data['name']}\n"
        f"Цвет: {profile_data['color']}"
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена создания профиля."""
    await update.message.reply_text("Создание профиля отменено.")
    return ConversationHandler.END


def main():
    # Загружаем сохранённые профили при запуске бота
    load_data()

    # Создаём приложение.
    # Замените TOKEN на токен вашего бота.
    application = Application.builder().token(TOKEN).build()

    # Диалог создания профиля
    conversation = ConversationHandler(
        entry_points=[
            CommandHandler("start", start)
        ],
        states={
            NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)
            ],
            COLOR: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_color)
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel)
        ],
    )

    application.add_handler(conversation)

    # Команда для просмотра сохранённого профиля
    application.add_handler(
        CommandHandler("profile", profile)
    )

    # Запускаем бота
    application.run_polling()


if __name__ == "__main__":
    main()

