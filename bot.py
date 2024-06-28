import telebot 
import os



bot_api=os.getenv("bot_api")
print(bot_api)
bot=telebot.TeleBot(token="7289171817:AAFUvQvcS6nHSEdXys7I7aRaCsLUbB2fd4A")

@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "Hello, Glad you texted!!")

@bot.message_handler(commands=["get_my_id"])
def get_my_id(message):
    bot.send_message(chat_id=message.chat.id,text=f"Your Chat id is : {message.chat.id}")

if __name__=="__main__":
    print("Bot is Live!!")
    bot.polling()