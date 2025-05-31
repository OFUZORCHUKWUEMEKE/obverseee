from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI
from contextlib import asynccontextmanager
import os


async def init_db():
    MONGO_URL= os.getenv("MONGO_URL=DATABASE_URL")
    client =AsyncIOMotorClient(MONGO_URL)
    db =client["obversee"]
    user_collection = db["users"]
    transaction_collection = db["transactions"]
    wallet_collection = db["wallets"]

    await user_collection.create_index("",unique=True)
    await wallet_collection.create_index("",unique=True)
    await transaction_collection.create_index("",unique=True)
    await payme




