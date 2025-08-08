from telegram import Bot
from database import get_birthdays_today, get_all_user_ids
from config import TOKEN
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
import asyncio

bot = Bot(token=TOKEN)


async def birthday_check():
    today = datetime.today().strftime("%m-%d")
    tomorrow = (datetime.today() + timedelta(days=1)).strftime("%m-%d")

    today_birthdays = get_birthdays_today(today)
    tomorrow_birthdays = get_birthdays_today(tomorrow)

    if not today_birthdays and not tomorrow_birthdays:
        return  # No birthdays, skip sending

    message_parts = []
    if today_birthdays:
        message_parts.append("🎉 Today is the birthday of:\n" + "\n".join(f"• {name}" for _, name in today_birthdays))
    if tomorrow_birthdays:
        message_parts.append("📅 Tomorrow is the birthday of:\n" + "\n".join(f"• {name}" for _, name in tomorrow_birthdays))

    message = "\n\n".join(message_parts)

    for user_id in get_all_user_ids():
        try:
            await bot.send_message(chat_id=user_id, text=message)
        except Exception as e:
            print(f"❗ Could not send message to {user_id}: {e}")


async def main():
    scheduler = AsyncIOScheduler()

    timezone = pytz.timezone("Europe/Brussels")

    trigger = CronTrigger(hour="0,8,16", timezone=timezone)
    scheduler.add_job(birthday_check, trigger=trigger)

    scheduler.start()

    print("Scheduler is running. Press Ctrl+C to stop.")
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
