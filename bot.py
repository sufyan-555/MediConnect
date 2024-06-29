import telebot
import os
import time
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, Table, select
from datetime import datetime, timedelta

load_dotenv()

bot_api = os.getenv("bot_api")
bot = telebot.TeleBot(token=bot_api)
db_url = 'sqlite:///./instance/users.db'
engine = create_engine(db_url)
metadata = MetaData()
metadata.reflect(bind=engine)
medicine_table = Table('medicine', metadata, autoload_with=engine)


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "Hello, Glad you texted!!")

@bot.message_handler(commands=["get_my_id"])
def get_my_id(message):
    bot.send_message(chat_id=message.chat.id, text=f"Your Chat id is : {message.chat.id}")

if __name__ == "__main__":
    print("MediConnect Bot is Live!!")
    bot.polling()
