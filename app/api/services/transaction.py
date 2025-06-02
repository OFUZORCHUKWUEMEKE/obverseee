from typing import List,Optional
from datetime import datetime,timedelta
from ..models.transaction import Transaction , TransactionStatus,TransactionType
from ..repositories.transaction import TransactionRepository
import logging
from beanie.odm.fields import PydanticObjectId

logger = logging.getLogger(__name__)

class TransactionService:
    def __init__(self, transaction_repo: TransactionRepository):
        self.repository = transaction_repo

    async def record_transaction(
        self,
        user_id: str,
        tx_type: TransactionType,
        chain: str,
        *,
        tx_hash: Optional[str] = None,
        from_address: Optional[str] = None,
        to_address: Optional[str] = None,
        token_address: Optional[str] = None,
        token_symbol: Optional[str] = None,
        amount: Optional[str] = None,
        usd_value: Optional[float] = None,
        gas_fee: Optional[str] = None
    ) -> Transaction:
        """
        Records a new transaction in the system
        """
        transaction = Transaction(
            user_id=user_id,
            tx_type=tx_type,
            chain=chain,
            tx_hash=tx_hash,
            from_address=from_address,
            to_address=to_address,
            token_address=token_address,
            token_symbol=token_symbol,
            amount=amount,
            usd_value=usd_value,
            gas_fee=gas_fee,
            status=TransactionStatus.PENDING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        try:
            created_tx = await self.repository.create(transaction)
            logger.info(f"Recorded new transaction {created_tx.id} for user {user_id}")
            return created_tx
        except Exception as e:
            logger.error(f"Failed to record transaction: {str(e)}")
            raise RuntimeError("Failed to record transaction") from e

    async def update_transaction_status(
        self,
        tx_id: str,
        status: TransactionStatus,
        confirmations: Optional[int] = None
    ) -> Optional[Transaction]:
        """
        Updates transaction status and confirmation count
        """
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        
        if status == TransactionStatus.CONFIRMED:
            update_data["confirmed_at"] = datetime.utcnow()
        
        if confirmations is not None:
            update_data["confirmations"] = confirmations

        try:
            updated_tx = await self.repository.update(tx_id, {"$set": update_data})
            if updated_tx:
                logger.info(f"Updated transaction {tx_id} to status {status}")
            return updated_tx
        except Exception as e:
            logger.error(f"Error updating transaction {tx_id}: {str(e)}")
            raise RuntimeError("Failed to update transaction") from e

    async def get_user_transactions(
        self,
        user_id: str,
        *,
        days: Optional[int] = None,
        limit: int = 100,
        tx_type: Optional[TransactionType] = None,
        status: Optional[TransactionStatus] = None
    ) -> List[Transaction]:
        """
        Retrieves transactions for a user with optional filters
        """
        query = {"user_id": user_id}
        
        if days:
            cutoff = datetime.utcnow() - timedelta(days=days)
            query["created_at"] = {"$gte": cutoff}
        
        if tx_type:
            query["tx_type"] = tx_type
            
        if status:
            query["status"] = status

        try:
            transactions = await self.repository.find_many(query, limit=limit)
            logger.debug(f"Fetched {len(transactions)} transactions for user {user_id}")
            return transactions
        except Exception as e:
            logger.error(f"Error fetching transactions for user {user_id}: {str(e)}")
            raise RuntimeError("Failed to fetch user transactions") from e

    async def find_transaction_by_hash(
        self,
        tx_hash: str
    ) -> Optional[Transaction]:
        """
        Finds a transaction by its blockchain hash
        """
        try:
            return await self.repository.get_by_tx_hash(tx_hash)
        except Exception as e:
            logger.error(f"Error finding transaction by hash {tx_hash}: {str(e)}")
            raise RuntimeError("Failed to find transaction by hash") from e

    async def process_transaction_webhooks(self) -> int:
        """
        Processes pending transaction webhooks (system task)
        Returns count of processed webhooks
        """
        try:
            pending_webhooks = await self.repository.get_pending_webhooks()
            count = 0
            
            for tx in pending_webhooks:
                # Here you would actually call the webhook URL
                # For simplicity, we'll just mark as processed
                await self.repository.update(
                    tx.id,
                    {"$set": {"webhook_processed": True}}
                )
                count += 1
                
            logger.info(f"Processed {count} transaction webhooks")
            return count
        except Exception as e:
            logger.error(f"Error processing transaction webhooks: {str(e)}")
            raise RuntimeError("Failed to process transaction webhooks") from e

    async def get_recent_transactions(
        self,
        hours: int = 24,
        limit: int = 1000
    ) -> List[Transaction]:
        """
        Gets recent transactions system-wide (for monitoring/analytics)
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        try:
            return await self.repository.find_many(
                {"created_at": {"$gte": cutoff}},
                limit=limit
            )
        except Exception as e:
            logger.error(f"Error fetching recent transactions: {str(e)}")
            raise RuntimeError("Failed to fetch recent transactions") from e
