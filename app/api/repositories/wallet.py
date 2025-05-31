from app.api.models.wallet import Wallet
from app.api.repositories.base import BaseRepository

class WalletRepository(BaseRepository[Wallet]):
    @property()
    def model(self):
        return Wallet