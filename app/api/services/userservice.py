from typing import Optional , List
from ..models.user import User
from ..repositories.user import UserRepository
from pydantic import EmailStr
from beanie.odm.fields import PydanticObjectId
from datetime import datetime
import logging

logging = logging.getLogger(__name__)

class UserService:
    def __init__(self,user_repository:UserRepository):
        self.repository = user_repository

    # async def create_user()
