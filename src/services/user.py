from typing import Optional
from sqlalchemy.orm import Session
from src.repositories.user import user_repo
from src.schemas.user import UserCreate, UserInDB
from src.config.logging import logger

class UserService:
    def create_user(self, db: Session, user_in: UserCreate) -> UserInDB:
        existing = user_repo.get_by_username(db, user_in.username)
        if existing:
            raise ValueError("Username already exists")
        
        try:
            user = user_repo.create(db, user_in.model_dump())
            return UserInDB.model_validate(user)
        except Exception as e:
            logger.exception("Failed to create user")
            raise

    def get_user(self, db: Session, username: str) -> Optional[UserInDB]:
        user = user_repo.get_by_username(db, username)
        if user:
            return UserInDB.model_validate(user)
        return None

user_service = UserService()
