from app.api.models.transaction import Transaction
from app.api.repositories.base import BaseRepository

class TransactionRepository(BaseRepository[Transaction]):
    @property()
    def model(self):
        return Transaction