import telebot 
import os



bot_api=os.getenv("bot_api")
bot=telebot.TeleBot(token=bot_api)

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message,"Hello, Glad you texted")


if __name__=="__main__":
    print("Basic Bot is Live :)")
    bot.polling()