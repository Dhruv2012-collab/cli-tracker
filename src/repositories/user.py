from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.models.user import User
from src.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        stmt = select(User).options(selectinload(User.tasks), selectinload(User.habits)).where(User.username == username)
        return db.scalar(stmt)

user_repo = UserRepository()
