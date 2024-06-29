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
from dotenv import load_dotenv
load_dotenv()

bot_api=os.getenv("bot_api")
bot=telebot.TeleBot(token="7289171817:AAFUvQvcS6nHSEdXys7I7aRaCsLUbB2fd4A")


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
    verbose=True,
    handle_parsing_errors=True
)


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "Hello, Glad you texted!!")

@bot.message_handler(commands=["get_my_id"])
def get_my_id(message):
    bot.send_message(chat_id=message.chat.id,text=f"Your Chat id is : {message.chat.id}")

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
    bot.polling()