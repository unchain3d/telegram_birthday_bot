import datetime
from datetime import datetime
import os
from config import TOKEN
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler
)
from database import add_birthday, get_birthdays, delete_birthday
from apscheduler.schedulers.asyncio import AsyncIOScheduler


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! Я бот-нагадувач про дні народження.\n"
        "📌 Використай:\n"
        "/add — щоб додати\n"
        "/list — список\n"
        "/delete — для видалення"
    )

NAME, DAY, MONTH, YEAR = range(4)


# Старт + ім'я
async def start_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введи ім'я:")
    return NAME


# День
async def ask_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Введи день народження:")
    return DAY


# Місяць
async def ask_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    day = update.message.text
    if not day.isdigit() or not (1 <= int(day) <= 31):
        await update.message.reply_text("❗ Введи коректний день (1–31):")
        return DAY
    context.user_data["day"] = int(day)
    await update.message.reply_text("Введи місяць народження:")
    return MONTH


# Рочок :3
async def ask_year(update: Update, context: ContextTypes.DEFAULT_TYPE):
    month = update.message.text
    if not month.isdigit() or not (1 <= int(month) <= 12):
        await update.message.reply_text("❗ Введи існуючий місяць (1–12):")
        return MONTH
    context.user_data["month"] = int(month)
    await update.message.reply_text("Введи рік народження:")
    return YEAR


# Запис в БД
async def save_birthday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    year = update.message.text
    if not year.isdigit():
        await update.message.reply_text("❗ Введи правильний рік:")
        return YEAR

    name = context.user_data["name"]
    day = context.user_data["day"]
    month = context.user_data["month"]

    try:
        date_obj = datetime.strptime(f"{day}.{month}.{year}", "%d.%m.%Y").date()
        add_birthday(update.effective_user.id, name, date_obj)
        await update.message.reply_text(f"🎉 Додано: {name}, {date_obj.strftime('%d.%m.%Y')}")
    except ValueError:
        await update.message.reply_text("❗ Некоректна дата. Спробуй ще раз команду /add")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Додавання скасовано.")
    return ConversationHandler.END


# Виводить усі Дні народження
async def list_birthdays(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bdays = get_birthdays(update.effective_user.id)
    if bdays:
        text = "\n".join([f"{name} — {date.strftime('%d.%m.%Y')}" for name, date in bdays])
    else:
        text = "Немає доданих днів народження."
    await update.message.reply_text(text)


# Видаляє
async def delete_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bdays = get_birthdays(update.effective_user.id)
    if not bdays:
        await update.message.reply_text("Список порожній.")
        return

    keyboard = [
        [InlineKeyboardButton(f"{name} — {date.strftime('%d.%m.%Y')}", callback_data=f"delete_{name}")]
        for name, date in bdays
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Вибери кого видалити:", reply_markup=reply_markup)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("delete_"):
        name = query.data.split("delete_")[1]
        delete_birthday(query.from_user.id, name)
        await query.edit_message_text(f"✅ Видалено: {name}")


# MAIN
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("add", start_add)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_day)],
            DAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_month)],
            MONTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_year)],
            YEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_birthday)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv_handler)

    app.add_handler(CommandHandler("list", list_birthdays))
    app.add_handler(CommandHandler("delete", delete_menu))  # лише кнопкова версія
    app.add_handler(CallbackQueryHandler(button_callback))

    app.run_polling()

if __name__ == "__main__":
    main()
