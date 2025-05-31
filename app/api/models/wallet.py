from datetime import datetime
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field
from bson import ObjectId
from pymongo import IndexModel

from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]

class ChainENUM(str, Enum):
    """Chain enumeration"""
    SOLANA = "solana"
    ETHEREUM = "ethereum"


class StableCoin(str, Enum):
    """Stable coin enumeration"""
    USDC = "usdc"
    USDT = "usdt"

class Token(BaseModel):
    """Token model embedded in Wallet"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    symbol: StableCoin = Field(..., description="Token symbol")
    balance: float = Field(default=0, description="Token balance")
    contractAddress: Optional[str] = Field(None, description="Token contract address")
    decimals: int = Field(default=6, description="Token decimals")
    createdAt: datetime = Field(default_factory=datetime.utcnow, description="Token creation timestamp")

    class Config:
        schema_extra = {
            "example": {
                "symbol": "usdc",
                "balance": 100.50,
                "contractAddress": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                "decimals": 6
            }
        }

class Wallet(BaseModel):
    """Wallet model for MongoDB with FastAPI"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: PyObjectId = Field(..., description="Telegram/Discord ID")
    chain: ChainENUM = Field(default=ChainENUM.SOLANA, description="Blockchain network")
    address: str = Field(..., description="Wallet address")
    encryptedPrivateKey: str = Field(..., description="Encrypted private key")
    tokens: List[Token] = Field(default_factory=list, description="Token balances")
    createdAt: datetime = Field(default_factory=datetime.utcnow, description="Wallet creation timestamp")
    updatedAt: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "chain": "solana",
                "address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
                "encryptedPrivateKey": "encrypted_key_here",
                "tokens": [
                    {
                        "symbol": "usdc",
                        "balance": 100.50,
                        "contractAddress": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                        "decimals": 6
                    }
                ]
            }
        }

class WalletResponse(BaseModel):
    """Wallet response model for API responses"""
    id: str = Field(..., description="Wallet document ID")
    user_id: str = Field(..., description="User ID reference")
    chain: ChainENUM
    address: str
    tokens: List[TokenResponse] = Field(default_factory=list)
    createdAt: datetime
    updatedAt: datetime

    class Config:
        schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439012",
                "chain": "solana",
                "address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
                "tokens": [
                    {
                        "symbol": "usdc",
                        "balance": 100.50,
                        "contractAddress": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                        "decimals": 6,
                        "createdAt": "2024-01-01T00:00:00Z"
                    }
                ],
                "createdAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-01T00:00:00Z"
            }
        }

