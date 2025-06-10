import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    TELEGRAM_BOT = os.getenv("TELEGRAM_BOT")
    # GEMINI=os.getenv("GOOGLE_API_KEY")
    MONGO_URI=os.getenv("MONGO_URL")

config = Config()