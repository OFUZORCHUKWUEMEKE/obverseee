from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Literal
from datetime import datetime
from bson import ObjectId
from pymongo import IndexModel
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]

class ChainENUM(str, Enum):
    """Chain enumeration - adjust values based on your needs"""
    SOLANA = "solana"
    ETHEREUM = "ethereum"

class StableCoin(str, Enum):
    """Stable coin enumeration"""
    USDC = "usdc"
    USDT = "usdt"

class Status(str, Enum):
    """Transaction status enumeration"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"


class PaymentLink(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    linkId: str = Field(default_factory=lambda: str(uuid4()), description="Unique link identifier")
    merchantUserId: str = Field(..., description="ID of the merchant user")
    amount: str = Field(..., description="Payment amount")
    tokenAddress: str = Field(..., description="Token contract address")
    tokenSymbol: str = Field(..., description="Token symbol")
    chain: ChainENUM = Field(..., description="Blockchain network")
    description: Optional[str] = None
    singleUse: bool = Field(default=False, description="Whether the link is single-use")
    expiresAt: Optional[datetime] = None
    webhookUrl: Optional[HttpUrl] = None
    redirectUrl: Optional[HttpUrl] = None
    status: Status = Field(default=Status.ACTIVE, description="Payment link status")
    paymentTxHash: Optional[str] = None
    paidAt: Optional[datetime] = None
    paidByUserId: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True
       