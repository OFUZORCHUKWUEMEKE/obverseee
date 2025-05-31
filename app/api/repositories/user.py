from app.api.models.user import User
from typing import Optional
from app.api.repositories.base import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    async def get_by_user_id(self,user_id:str)->Optional[User]:
        return await self.find_one({"user_id":user_id})
    
    async def get_by_username(self,username:str)->Optional[User]:
        return await self.find_one({"username":username})
    
    async def update_wallet(self,user_id:str,wallet_data:dict)->Optional[User]:
        return await self.update(user_id,{"$set":{"wallets":wallet_data}})

    async def update_notification_preference(self,user_id:str,enabled:bool)->Optional[User]:
        return await self.update(user_id,{"$set":{"notification_enabled":enabled}})