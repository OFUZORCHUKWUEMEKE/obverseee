from app.api.repositories.base import BaseRepository
from app.api.models.paymentlink import PaymentLink
from typing import Optional, List
from datetime import datetime, timedelta

class PaymentLinkRepository(BaseRepository[PaymentLink]):
    def __init__(self):
        super().__init__(PaymentLink)

    async def get_by_link_id(self, link_id: str) -> Optional[PaymentLink]:
        return await self.find_one({"link_id": link_id})

    async def get_active_links_by_merchant(
        self,
        merchant_user_id: str
    ) -> List[PaymentLink]:
        return await self.find_many({
            "merchant_user_id": merchant_user_id,
            "status": "active",
            "$or": [
                {"expires_at": {"$gt": datetime.utcnow()}},
                {"expires_at": None}
            ]
        })

    async def get_expired_links(self) -> List[PaymentLink]:
        return await self.find_many({
            "expires_at": {"$lt": datetime.utcnow()},
            "status": "active"
        })
    async def mark_as_paid(
        self,
        link_id: str,
        tx_hash: str,
        paid_by_user_id: str
    ) -> Optional[PaymentLink]:
        return await self.update(
            link_id,
            {
                "$set": {
                    "status": "paid",
                    "payment_tx_hash": tx_hash,
                    "paid_by_user_id": paid_by_user_id,
                    "paid_at": datetime.utcnow()
                }
            }
        )

    async def cancel_link(self, link_id: str) -> Optional[PaymentLink]:
        return await self.update(
            link_id,
            {"$set": {"status": "cancelled"}}
        )

    async def get_links_ready_for_webhook(self) -> List[PaymentLink]:
        return await self.find_many({
            "status": "paid",
            "webhook_url": {"$ne": None},
            "webhook_sent": {"$ne": True}
        })

    async def mark_webhook_sent(self, link_id: str) -> Optional[PaymentLink]:
        return await self.update(
            link_id,
            {"$set": {"webhook_sent": True}}
        )

