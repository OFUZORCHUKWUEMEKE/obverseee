from app.api.models.user import User
from app.api.repositories.base import BaseRepository

class UserRepository(BaseRepository[User]):
    @property()
    def model(self):
        return User

