from app.api.repositories.base import BaseRepository
from app.api.models.paymentlink import PaymentLink

class PaymentLinkRepository(BaseRepository[PaymentLink]):
    @property
    def model(self):
        return PaymentLink

    async def get_by_link_id(self, link_id: str) -> Optional[PaymentLink]:
        try:
            item = await self.collection.find_one({"linkId": link_id})
            if item:
                item['_id'] = str(item['_id'])
                return self.model(**item)
            return None
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving payment link: {str(e)}")