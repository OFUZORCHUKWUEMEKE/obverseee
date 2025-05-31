from datetime import datetime
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field
from bson import ObjectId
from pymongo import IndexModel

from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]


class ChainEnum(str, Enum):
    """Blockchain network enumeration"""
    SOLANA = "solana"
    ETHEREUM = "ethereum"


class TransactionTypeEnum(str, Enum):
    """Transaction type enumeration"""
    BUY = "buy"
    SELL = "sell"
    SEND = "send"
    RECEIVE = "receive"


class TransactionStatusEnum(str, Enum):
    """Transaction status enumeration"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"

class Transaction(BaseModel):
    """Transaction model for MongoDB with FastAPI"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    userId: str = Field(..., description="User identifier")
    txHash: Optional[str] = Field(None, description="Transaction hash")
    chain: ChainEnum = Field(..., description="Blockchain network")
    txType: TransactionTypeEnum = Field(..., description="Transaction type")
    
    # Transaction details
    fromAddress: Optional[str] = Field(None, description="Sender address")
    toAddress: Optional[str] = Field(None, description="Recipient address")
    tokenAddress: Optional[str] = Field(None, description="Token contract address")
    tokenSymbol: Optional[str] = Field(None, description="Token symbol")
    amount: Optional[str] = Field(None, description="Transaction amount as string for precision")
    usdValue: Optional[float] = Field(None, description="USD value of transaction")
    
    # Status tracking
    status: TransactionStatusEnum = Field(default=TransactionStatusEnum.PENDING, description="Transaction status")
    confirmations: int = Field(default=0, description="Number of confirmations")
    gasFee: Optional[str] = Field(None, description="Gas fee as string for precision")
    confirmedAt: Optional[datetime] = Field(None, description="Confirmation timestamp")
    
    # Timestamps
    createdAt: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updatedAt: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "userId": "123456789",
                "txHash": "5wHhz3KWqnLpCQK7Q8CvG7q8WJVwCJQKCQk7wHhz3KWqnLpCQK7Q8",
                "chain": "solana",
                "txType": "send",
                "fromAddress": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
                "toAddress": "8yBJBWKJ9XnBJrj8v7GsdBfYNPQk7BZ9vhG3tGJZsT9Q",
                "tokenAddress": "So11111111111111111111111111111111111111112",
                "tokenSymbol": "SOL",
                "amount": "1.5",
                "usdValue": 150.75,
                "status": "confirmed",
                "confirmations": 32,
                "gasFee": "0.000005",
                "confirmedAt": "2024-01-01T12:00:00Z"
            }
        }

class TransactionResponse(BaseModel):
    """Transaction response model for API responses"""
    id: str = Field(..., description="Transaction document ID")
    userId: str
    txHash: Optional[str] = None
    chain: ChainEnum
    txType: TransactionTypeEnum
    fromAddress: Optional[str] = None
    toAddress: Optional[str] = None
    tokenAddress: Optional[str] = None
    tokenSymbol: Optional[str] = None
    amount: Optional[str] = None
    usdValue: Optional[float] = None
    status: TransactionStatusEnum
    confirmations: int
    gasFee: Optional[str] = None
    confirmedAt: Optional[datetime] = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "userId": "123456789",
                "txHash": "5wHhz3KWqnLpCQK7Q8CvG7q8WJVwCJQKCQk7wHhz3KWqnLpCQK7Q8",
                "chain": "solana",
                "txType": "send",
                "fromAddress": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
                "toAddress": "8yBJBWKJ9XnBJrj8v7GsdBfYNPQk7BZ9vhG3tGJZsT9Q",
                "tokenAddress": "So11111111111111111111111111111111111111112",
                "tokenSymbol": "SOL",
                "amount": "1.5",
                "usdValue": 150.75,
                "status": "confirmed",
                "confirmations": 32,
                "gasFee": "0.000005",
                "confirmedAt": "2024-01-01T12:00:00Z",
                "createdAt": "2024-01-01T10:00:00Z",
                "updatedAt": "2024-01-01T12:00:00Z"
            }
        }

class TransactionCreate(BaseModel):
    """Model for creating new transactions"""
    userId: str = Field(..., description="User identifier")
    txHash: Optional[str] = None
    chain: ChainEnum = Field(..., description="Blockchain network")
    txType: TransactionTypeEnum = Field(..., description="Transaction type")
    fromAddress: Optional[str] = None
    toAddress: Optional[str] = None
    tokenAddress: Optional[str] = None
    tokenSymbol: Optional[str] = None
    amount: Optional[str] = None
    usdValue: Optional[float] = None
    status: TransactionStatusEnum = TransactionStatusEnum.PENDING
    confirmations: int = 0
    gasFee: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "userId": "123456789",
                "chain": "solana",
                "txType": "send",
                "fromAddress": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
                "toAddress": "8yBJBWKJ9XnBJrj8v7GsdBfYNPQk7BZ9vhG3tGJZsT9Q",
                "tokenSymbol": "SOL",
                "amount": "1.5",
                "usdValue": 150.75
            }
        }