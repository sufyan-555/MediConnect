import telebot 
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.agents import Tool
import pypdf
from langchain.agents import initialize_agent
import os
import time
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, Table, select,and_
from datetime import datetime
import threading
import base64

load_dotenv()

bot_api=os.getenv("bot_api")
bot=telebot.TeleBot(token=bot_api)




GOOGLE_API_KEY=os.getenv('GOOGLE_API_KEY')

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001",google_api_key=GOOGLE_API_KEY)
database_dir="Database"
db=Chroma(
    persist_directory="Database",
    embedding_function=embeddings
)
retriver=db.as_retriever()

rag_tool=Tool(
    name="Rag_tool",
    func=retriver.get_relevant_documents,
    description="this tool is recommended for getting home remedies for acute health problems and if answer is not provided, use duckduckgo search tool"
)

search=DuckDuckGoSearchRun()

model = ChatGoogleGenerativeAI(model="gemini-pro")

agent=initialize_agent(
    llm=model,
    tools=[search,rag_tool],
    verbose=False,
    handle_parsing_errors=True
)

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
            chat_id = row[3]
            medicine_name = row[1]
            img_data=row[12]

            if img_data:
                #img_data=base64.b64encode(img_data).decode('utf-8')
                try:
                    bot.send_photo(chat_id=chat_id, photo=img_data)
                except Exception as e:
                    print(f"Attempt failed: {e}")
            
            bot.send_message(chat_id=chat_id, text=f"Reminder: It's time to take your medicine: {medicine_name}")

        # Sleep for 60 seconds before checking again
        time.sleep(61)

@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "Hello, Glad you texted!!")

@bot.message_handler(commands=["get_my_id"])
def get_my_id(message):
    bot.send_message(chat_id=message.chat.id, text=f"Your Chat id is : {message.chat.id}")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text.startswith('/'):
        return
    try:
        response = agent.invoke(message.text).content
        bot.reply_to(message, response, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"Sorry, something went wrong")

if __name__=="__main__":
    print("MediConnect Bot is Live!!")
    reminder_thread = threading.Thread(target=send_reminders)
    reminder_thread.start()
    bot.polling()
