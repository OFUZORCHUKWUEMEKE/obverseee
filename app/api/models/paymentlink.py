from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field
from pymongo import IndexModel
from beanie import Document, Indexed


class Chain(str, Enum):
    SOLANA = "solana"
    ETHEREUM = "ethereum"


class Status(str, Enum):
    ACTIVE = "active"
    PAID = "paid"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class PaymentLink(Document):
    link_id: str = Field(..., unique=True)
    merchant_user_id: str
    
    # Payment details
    amount: str
    token_address: str
    token_symbol: str
    chain: Chain
    
    description: Optional[str] = None
    
    # Link configuration
    single_use: bool = False
    expires_at: Optional[datetime] = None
    webhook_url: Optional[str] = None
    redirect_url: Optional[str] = None
    
    # Status tracking
    status: Status = Status.ACTIVE
    payment_tx_hash: Optional[str] = None
    paid_at: Optional[datetime] = None
    paid_by_user_id: Optional[str] = None
    
    class Settings:
        name = "payment_links"
        indexes = [
            IndexModel("link_id", unique=True),
            IndexModel("merchant_user_id"),
            IndexModel("status"),
            IndexModel("expires_at", expireAfterSeconds=0),  # For TTL
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "link_id": "unique-link-123",
                "merchant_user_id": "user-123",
                "amount": "10.5",
                "token_address": "0x...",
                "token_symbol": "USDC",
                "chain": Chain.ETHEREUM,
                "description": "Payment for services",
                "single_use": True,
                "expires_at": "2023-12-31T23:59:59",
                "webhook_url": "https://example.com/webhook",
                "redirect_url": "https://example.com/thank-you",
                "status": Status.ACTIVE
            }
        }


class PaymentLinkCreate(BaseModel):
    merchant_user_id: str
    amount: str
    token_address: str
    token_symbol: str
    chain: Chain
    description: Optional[str] = None
    single_use: bool = False
    expires_at: Optional[datetime] = None
    webhook_url: Optional[str] = None
    redirect_url: Optional[str] = None


class PaymentLinkUpdate(BaseModel):
    status: Optional[Status] = None
    payment_tx_hash: Optional[str] = None
    paid_at: Optional[datetime] = None
    paid_by_user_id: Optional[str] = None


class PaymentLinkResponse(PaymentLink):
    class Config:
        from_attributes = True