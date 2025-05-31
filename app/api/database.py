from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL= os.getenv("MONGO_URL=DATABASE_URL")
client =AsyncIOMotorClient(MONGO_URL)

db =client["obversee"]