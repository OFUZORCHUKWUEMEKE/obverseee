from typing import Optional ,List
from datetime import datetime
from ..models.paymentlink import PaymentLink
from ..repositories.paymentlink import PaymentLinkRepository
from pydantic import HttpUrl
import secrets
import logging
from beanie.odm.fields import PydanticObjectId

logger = logging.getLogger(__name__)

class PaymentLinkService:
    def __init__(self, payment_link_repo: PaymentLinkRepository):
        self.repository = payment_link_repo

    async def create_payment_link(
        self,
        merchant_user_id: str,
        amount: str,
        token_address: str,
        token_symbol: str,
        chain: str,
        *,
        description: Optional[str] = None,
        single_use: bool = True,
        expires_in_hours: Optional[int] = None,
        webhook_url: Optional[HttpUrl] = None,
        redirect_url: Optional[HttpUrl] = None
    ) -> PaymentLink:
        """
        Creates a new payment link with automatic ID generation
        """
        link_id = f"pl_{secrets.token_urlsafe(12)}"
        expires_at = None
        
        if expires_in_hours:
            expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)

        payment_link = PaymentLink(
            link_id=link_id,
            merchant_user_id=merchant_user_id,
            amount=amount,
            token_address=token_address,
            token_symbol=token_symbol,
            chain=chain,
            description=description,
            single_use=single_use,
            expires_at=expires_at,
            webhook_url=str(webhook_url) if webhook_url else None,
            redirect_url=str(redirect_url) if redirect_url else None,
            status=PaymentLinkStatus.ACTIVE,
            created_at=datetime.utcnow()
        )

        try:
            created_link = await self.repository.create(payment_link)
            logger.info(f"Created payment link {link_id} for merchant {merchant_user_id}")
            return created_link
        except Exception as e:
            logger.error(f"Failed to create payment link: {str(e)}")
            raise RuntimeError("Failed to create payment link") from e

    async def get_payment_link(self, link_id: str) -> Optional[PaymentLink]:
        """
        Retrieves a payment link by its ID
        """
        try:
            link = await self.repository.get_by_link_id(link_id)
            if link and self._is_link_expired(link):
                await self._handle_expired_link(link)
                return None
            return link
        except Exception as e:
            logger.error(f"Error fetching payment link {link_id}: {str(e)}")
            raise RuntimeError("Failed to fetch payment link") from e

    async def process_payment_confirmation(
        self,
        link_id: str,
        tx_hash: str,
        paid_by_user_id: str
    ) -> Optional[PaymentLink]:
        """
        Marks a payment link as paid and records transaction details
        """
        try:
            link = await self.get_payment_link(link_id)
            if not link:
                raise ValueError("Payment link not found or expired")
            
            if link.status != PaymentLinkStatus.ACTIVE:
                raise ValueError(f"Payment link is {link.status}, cannot mark as paid")
            
            updated_link = await self.repository.mark_as_paid(
                link_id,
                tx_hash,
                paid_by_user_id
            )
            
            logger.info(f"Payment link {link_id} marked as paid with tx {tx_hash}")
            return updated_link
        except ValueError as e:
            logger.warning(f"Payment confirmation failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error confirming payment for link {link_id}: {str(e)}")
            raise RuntimeError("Failed to confirm payment") from e

    async def cancel_payment_link(self, link_id: str) -> Optional[PaymentLink]:
        """
        Cancels an active payment link
        """
        try:
            link = await self.get_payment_link(link_id)
            if not link:
                raise ValueError("Payment link not found")
                
            if link.status != PaymentLinkStatus.ACTIVE:
                raise ValueError(f"Cannot cancel link with status {link.status}")
                
            cancelled_link = await self.repository.cancel_link(link_id)
            logger.info(f"Cancelled payment link {link_id}")
            return cancelled_link
        except ValueError as e:
            logger.warning(f"Link cancellation failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error cancelling payment link {link_id}: {str(e)}")
            raise RuntimeError("Failed to cancel payment link") from e

    async def get_merchant_links(
        self,
        merchant_user_id: str,
        active_only: bool = True
    ) -> List[PaymentLink]:
        """
        Retrieves all payment links for a merchant
        """
        try:
            if active_only:
                return await self.repository.get_active_links_by_merchant(merchant_user_id)
            return await self.repository.find_many({"merchant_user_id": merchant_user_id})
        except Exception as e:
            logger.error(f"Error fetching links for merchant {merchant_user_id}: {str(e)}")
            raise RuntimeError("Failed to fetch merchant links") from e

    async def process_expired_links(self) -> int:
        """
        System task to expire old links (run periodically)
        Returns count of expired links
        """
        try:
            expired_links = await self.repository.get_expired_links()
            count = 0
            for link in expired_links:
                await self.repository.update(
                    link.id,
                    {"$set": {"status": PaymentLinkStatus.EXPIRED}}
                )
                count += 1
            logger.info(f"Processed {count} expired payment links")
            return count
        except Exception as e:
            logger.error(f"Error processing expired links: {str(e)}")
            raise RuntimeError("Failed to process expired links") from e

    def _is_link_expired(self, link: PaymentLink) -> bool:
        """Helper to check if link is expired"""
        return (
            link.expires_at is not None 
            and link.expires_at < datetime.utcnow()
            and link.status == PaymentLinkStatus.ACTIVE
        )

    async def _handle_expired_link(self, link: PaymentLink) -> None:
        """Automatically expire links when fetched if needed"""
        try:
            await self.repository.update(
                link.id,
                {"$set": {"status": PaymentLinkStatus.EXPIRED}}
            )
            logger.info(f"Auto-expired payment link {link.link_id}")
        except Exception as e:
            logger.error(f"Failed to auto-expire link {link.link_id}: {str(e)}")