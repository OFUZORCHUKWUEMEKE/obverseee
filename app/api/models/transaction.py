from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from beanie import Document
from bson import ObjectId

class Chain(str, Enum):
    SOLANA = "solana"
    ETHEREUM = "ethereum"

class TransactionType(str, Enum):
    BUY = "buy"
    SELL = "sell"
    SEND = "send"
    RECEIVE = "receive"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"

class Transaction(Document):
    user_id: str
    tx_hash: Optional[str] = None
    chain: Chain
    tx_type: TransactionType
    
    # Transaction details
    from_address: Optional[str] = None
    to_address: Optional[str] = None
    token_address: Optional[str] = None
    token_symbol: Optional[str] = None
    amount: Optional[str] = None  # String to handle large numbers
    usd_value: Optional[float] = None
    
    # Status tracking
    status: TransactionStatus = TransactionStatus.PENDING
    confirmations: int = 0
    gas_fee: Optional[str] = None
    confirmed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "transactions"
        indexes = [
            "user_id",
            "tx_hash",
            "chain",
            "tx_type",
            "status",
            "created_at",
        ]

    class Config:
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "user_id": "user123",
                "tx_hash": "5VERv8NMvzbJMEkV8xnrLkEaWRtSz9CosKDYjCJjBRnb",
                "chain": Chain.SOLANA,
                "tx_type": TransactionType.SEND,
                "from_address": "HN5Hn1uVAf1sQ4Z1z8Gj3P5W5JrQeC5wXaJ4rYqk2FdT",
                "to_address": "2Qqh3G6tYr6T4ZQ1Xg7J7Kz8Xq1ZJ8Xq1ZJ8Xq1ZJ8Xq1Z",
                "token_address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                "token_symbol": "USDC",
                "amount": "10.5",
                "usd_value": 10.5,
                "status": TransactionStatus.PENDING,
                "confirmations": 0,
                "gas_fee": "0.0001",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        }

# Pydantic models for API
class TransactionCreate(BaseModel):
    user_id: str
    chain: Chain
    tx_type: TransactionType
    from_address: Optional[str] = None
    to_address: Optional[str] = None
    token_address: Optional[str] = None
    token_symbol: Optional[str] = None
    amount: Optional[str] = None
    usd_value: Optional[float] = None
    gas_fee: Optional[str] = None

class TransactionUpdate(BaseModel):
    status: Optional[TransactionStatus] = None
    tx_hash: Optional[str] = None
    confirmations: Optional[int] = None
    confirmed_at: Optional[datetime] = None
    usd_value: Optional[float] = None

class TransactionResponse(Transaction):
    class Config:
        fields = {'updated_at': {'exclude': True}}  # Optionally exclude fields from response