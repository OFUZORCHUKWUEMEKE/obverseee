from typing import Optional , List
from ..models.user import User
from ..repositories.user import UserRepository
from pydantic import EmailStr
from beanie.odm.fields import PydanticObjectId
from datetime import datetime
from ..models.wallet import Chain
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self,user_repository:UserRepository):
        self.repository = user_repository
    
    async def create_user(self,user_id:str,username:Optional[EmailStr]=None,default_chain:str=Chain.SOLANA):
        """
        Creates a new User with basic profile
        """
        existing_user = await self.repository.get_by_user_id(user_id=user_id)
        if existing_user:
            logger.warning(f"User creation failed - already exixts :{user_id}")
            raise ValueError(f"User with ID {user_id} already exists")
        user_data={
            "user_id":user_id,
            "username":username,
            "default_chain":default_chain,
            "created_at":datetime.utcnow()
        }
        try:
            new_user = User(**user_data)
            created_user = await self.repository.create(new_user)
            logger.info(f"Created new user :{user_id}")
            return created_user
        except Exception as e:
            logger.error(f"Error creating user {user_id} : {str(e)}")
            raise RuntimeError("Failed to create user") from e

    
    async def get_user(self,user_id:str)->Optional[User]:
        """
        Retrieves a user by their ID
        """
        try:
            return await self.repository.get_by_user_id(user_id)
        except Exception as e:
            logger.error(f"Error fetching user {user_id}:{str(e)}")
            raise RuntimeError("Failed to fetch user") from e
    

    async def update_user_profile(
        self,
        user_id: str,
        *,
        username: Optional[str] = None,
        email: Optional[EmailStr] = None,
        default_chain: Optional[str] = None,
        notification_enabled: Optional[bool] = None
    ) -> Optional[User]:
        """
        Updates user profile information
        """
        update_data = {}
        if username is not None:
            update_data["username"] = username
        if email is not None:
            update_data["email"] = email
        if default_chain is not None:
            update_data["default_chain"] = default_chain
        if notification_enabled is not None:
            update_data["notification_enabled"] = notification_enabled

        if not update_data:
            raise ValueError("No valid fields provided for update")
            
        try:
            updated_user = await self.repository.update(user_id, {"$set": update_data})
            if updated_user:
                logger.info(f"Updated profile for user: {user_id}")
            return updated_user
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {str(e)}")
            raise RuntimeError("Failed to update user") from e
    
    async def add_wallet_to_user(
        self,
        user_id: str,
        wallet_id: PydanticObjectId
    ) -> Optional[User]:
        """
        Associates a wallet with a user
        """
        try:
            return await self.repository.update(
                user_id,
                {"$addToSet": {"wallets": wallet_id}}
            )
        except Exception as e:
            logger.error(f"Error adding wallet to user {user_id}: {str(e)}")
            raise RuntimeError("Failed to add wallet to user") from e

    
    async def get_users_by_wallet_address(
        self,
        address: str,
        chain: Optional[str] = None
    ) -> List[User]:
        """
        Finds users associated with a specific wallet address
        """
        try:
            query = {"wallets.address": address}
            if chain:
                query["wallets.chain"] = chain
            return await self.repository.find_many(query)
        except Exception as e:
            logger.error(f"Error finding users by wallet {address}: {str(e)}")
            raise RuntimeError("Failed to find users by wallet") from e


    async def toggle_notifications(
        self,
        user_id: str,
        enabled: bool
    ) -> Optional[User]:
        """
        Toggles notification preferences for a user
        """
        try:
            return await self.repository.update_notification_preference(user_id, enabled)
        except Exception as e:
            logger.error(f"Error toggling notifications for user {user_id}: {str(e)}")
            raise RuntimeError("Failed to update notification preferences") from e

    
       
    