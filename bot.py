import telebot
import os
import time
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, Table, select,and_
from datetime import datetime
import threading

load_dotenv()

bot_api = os.getenv("bot_api")
bot = telebot.TeleBot(token=bot_api)

db_url = 'sqlite:///./instance/users.db'
engine = create_engine(db_url)
metadata = MetaData()
metadata.reflect(bind=engine)
medicine_table = Table('medicine', metadata, autoload_with=engine)



def send_reminders():
    while True:
        # Get current time and weekday
        current_time = datetime.now().strftime("%H:%M")
        current_weekday = datetime.now().strftime("%A").lower()  # e.g., 'monday'

        # Create the query
        query = select(medicine_table).where(
            and_(
                medicine_table.c.time == current_time,
                getattr(medicine_table.c, current_weekday) == True
            )
        )

        # Execute the query and fetch results
        with engine.connect() as conn:
            results = conn.execute(query).fetchall()

        # Send reminder messages
        for row in results:
            chat_id = row[3]  # Adjust this according to your table structure
            medicine_name = row[1]  # Adjust this according to your table structure
            bot.send_message(chat_id=chat_id, text=f"Reminder: It's time to take your medicine: {medicine_name}")

        # Sleep for 60 seconds before checking again
        time.sleep(61)

@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "Hello, Glad you texted!!")

@bot.message_handler(commands=["get_my_id"])
def get_my_id(message):
    bot.send_message(chat_id=message.chat.id, text=f"Your Chat id is : {message.chat.id}")

if __name__ == "__main__":
    print("MediConnect Bot is Live!!")
    reminder_thread = threading.Thread(target=send_reminders)
    reminder_thread.start()
    bot.polling()
