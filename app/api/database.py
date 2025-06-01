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
    MONGO_URL= os.getenv("MONGO_URL")
    client =AsyncIOMotorClient(MONGO_URL)
    await init_beanie(database=client.db_name,document_models=[Wallet,PaymentLink,Transaction,User])




