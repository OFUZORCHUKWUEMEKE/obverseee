from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.models.wallet import Wallet
from app.models.paymentlink import PaymentLink
from app.models.transaction import Transaction
from app.models.user import User


async def init_db():
    MONGO_URL= os.getenv("MONGO_URL=DATABASE_URL")
    client =AsyncIOMotorClient(MONGO_URL)
    await init_beanie(database=client.db_name,document_models=[Wallet,PaymentLink,Transaction,User])




