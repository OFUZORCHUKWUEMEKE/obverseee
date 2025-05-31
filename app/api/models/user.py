from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from pymongo import IndexModel
from beanie import Document, Link
from bson import ObjectId
from app.api.models.wallet import Wallet

class Chain(str, Enum):
    SOLANA = "solana"
    ETHEREUM = "ethereum"



class User(Document):
    user_id: str = Field(..., unique=True)  # telegram/discord ID
    username: Optional[str] = None
    wallets: List[Link[Wallet]] = Field(default_factory=list)
    default_chain: str = "solana"
    notification_enabled: bool = True
    
    class Settings:
        name = "users"
        indexes = [
            IndexModel("user_id", unique=True)
        ]