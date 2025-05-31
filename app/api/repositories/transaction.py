from app.api.models.transaction import Transaction
from app.api.repositories.base import BaseRepository
from typing import List
from datetime import datetime

class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self):
        super().__init__(Transaction)

    async def get_by_user_id(self, user_id: str, limit: int = 100) -> List[Transaction]:
        return await self.find_many({"user_id": user_id}, limit=limit)

    async def get_by_tx_hash(self, tx_hash: str) -> Optional[Transaction]:
        return await self.find_one({"tx_hash": tx_hash})

    async def get_recent_transactions(self, days: int = 7) -> List[Transaction]:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return await self.find_many({"created_at": {"$gte": cutoff_date}})

    async def update_status(self, tx_id: str, status: str) -> Optional[Transaction]:
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        if status == "confirmed":
            update_data["confirmed_at"] = datetime.utcnow()
        return await self.update(tx_id, {"$set": update_data})