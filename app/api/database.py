from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from .models.wallet import Wallet
from .models.paymentlink import PaymentLink
from .models.transaction import Transaction
from .models.user import User
from dotenv import load_dotenv
import os

load_dotenv()

async def init_db():
    MONGO_URL= os.getenv("MONGO_URL=DATABASE_URL")
    print(f"mongo url ${MONGO_URL}")
    client =AsyncIOMotorClient("mongodb+srv://ofuzor:ofuzor2018@cluster0.qjl8f.mongodb.net/obversee?retryWrites=true&w=majority")
    await init_beanie(database=client.db_name,document_models=[Wallet,PaymentLink,Transaction,User])




