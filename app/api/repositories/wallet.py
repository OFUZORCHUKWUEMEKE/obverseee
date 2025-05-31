from app.api.models.wallet import Wallet
from app.api.repositories.base import BaseRepository
from bson import ObjectId

class WalletRepository(BaseRepository[Wallet]):
    def __init__(self):
        super().__init__(Wallet)

    async def get_by_address(self,address:str)->Optional[Wallet]:
        return await self.find_one({"address":address})
    
    async def get_by_user_and_chain(self,user_id:str,chain:str)->list[Wallet]:
        return await self.find_many({
            "user_id":ObjectId(user_id),
            "chain":chain
        })
    
    async def add_token_to_wallet(self,wallet_id:str,token_data:dict)->Optional[Wallet]:
        return await self.update(wallet_id,{"$push":{"token":token_data}})

    async def update_token_balance(
        self,
        wallet_id: str,
        token_symbol: str,
        new_balance: str
    ) -> Optional[Wallet]:
        return await self.update(
            wallet_id,
            {"$set": {"tokens.$[elem].balance": new_balance}},
            array_filters=[{"elem.symbol": token_symbol}]
        )

    async def get_wallets_with_token(
        self,
        user_id: str,
        token_symbol: str
    ) -> List[Wallet]:
        return await self.find_many({
            "user_id": ObjectId(user_id),
            "tokens.symbol": token_symbol
        })