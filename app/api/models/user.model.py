
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
    """Chain enumeration - adjust values based on your needs"""
    SOLANA = "solana"
    ETHEREUM = "ethereum"

class User(BaseModel):
    """User model for MongoDB with FastAPI"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    userId: str = Field(..., description="Telegram/Discord ID", unique=True)
    username: Optional[str] = Field(None, description="Username")
    wallets: List[PyObjectId] = Field(default_factory=list, description="Referenced wallet ObjectIds")
    defaultChain: str = Field(default="solana", description="Default blockchain")
    notificationEnabled: bool = Field(default=True, description="Notification preferences")
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "userId": "123456789",
                "username": "john_doe",
                "wallets": [],
                "defaultChain": "solana",
                "notificationEnabled": True
            }
        }


