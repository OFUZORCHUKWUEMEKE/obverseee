from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
from beanie import Document, Indexed
from bson import ObjectId
from pymongo import IndexModel
from beanie.odm.fields import PydanticObjectId

class Chain(str, Enum):
    SOLANA = "solana"
    ETHEREUM = "ethereum"

class StableCoin(str, Enum):
    USDC = "usdc"
    USDT = "usdt"

class Token(BaseModel):
    symbol: StableCoin
    balance: float = 0.0
    contract_address: Optional[str] = None
    decimals: int = 6

class Wallet(Document):
    user_id: Indexed(PydanticObjectId)  # Reference to User document
    chain: Chain = Chain.SOLANA
    address: str
    encrypted_private_key: str
    tokens: List[Token] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "wallets"
        indexes = [
            [("user_id", 1), ("chain", 1), ("address", 1)],  # Compound index
            [("address", 1)],  # Single field index
        ]

    class Config:
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "chain": Chain.SOLANA,
                "address": "HN5Hn1uVAf1sQ4Z1z8Gj3P5W5JrQeC5wXaJ4rYqk2FdT",
                "encrypted_private_key": "encrypted_data_here",
                "tokens": [
                    {
                        "symbol": StableCoin.USDC,
                        "balance": 100.0,
                        "contract_address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                        "decimals": 6
                    }
                ],
                "created_at": datetime.utcnow()
            }
        }

# Pydantic models for API requests/responses
class TokenCreate(BaseModel):
    symbol: StableCoin
    contract_address: Optional[str] = None
    decimals: int = 6

class WalletCreate(BaseModel):
    user_id: str
    chain: Chain = Chain.SOLANA
    address: str
    encrypted_private_key: str
    tokens: List[TokenCreate] = Field(default_factory=list)

class WalletUpdate(BaseModel):
    tokens: Optional[List[TokenCreate]] = None
    encrypted_private_key: Optional[str] = None

class WalletResponse(Wallet):
    class Config:
        json_encoders = {ObjectId: str}
        allow_population_by_field_name = True
        fields = {'encrypted_private_key': {'exclude': True}}  # Don't expose private key in responses