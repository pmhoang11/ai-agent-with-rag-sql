from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.base import get_session
from app.models.user import User
from app.schemas.user_request import UserRequest

oauth2_schema = OAuth2PasswordBearer(tokenUrl='/service-auth/authorize')


def get_current_user_info(token: str = Depends(oauth2_schema)) -> dict:
    return UsersService.verify_token(token)


class UsersService:
    """User's service for interacting with the database."""

    def __init__(self) -> None:
        self.session = next(get_session())

    def __del__(self):
        self.session.close()  # Ensure the session is closed when the object is destroyed

    def check_username_conflict(self, username: str) -> None:
        """Checks if there exists user with given username.
        Args:
            username: username.
        """
        try:
            self.get_user_by_name(username)
        except HTTPException:
            return
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Already exists'
            )

    def register(self, username: str, password_text: str) -> None:
        """Adds new user to the database.
        Args:
            username: username.
            password_text: string password.
        """
        self.check_username_conflict(username)
        user = User(
            username=username,
            password_hashed=self.hash_password(password_text),
        )
        self.session.add(user)
        self.session.commit()

    def get_all_users(self) -> list[User]:
        """Returns all users.
        Returns:
            list[User]: list of users.
        """
        users = (
            self.session
            .query(User)
            .order_by(User.id.desc())
            .all()
        )
        return users

    def get_user_by_id(self, user_id: int) -> User:
        """Finds user by given user_id.
        Args:
            user_id: user id.
        Returns:
            User: found user.
        """
        user = (
            self.session
            .query(User)
            .filter(User.id == user_id)
            .first()
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    def get_user_by_name(self, username: str) -> User:
        """Finds user by given username.
        Args:
            username: username.
        Returns:
            User: found user.
        """
        user = (
            self.session
            .query(User)
            .filter(User.username == username)
            .first()
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    def add_user(self, user_schema: UserRequest, super_user_id: int) -> User:
        """Creates user by given user schema and saves it in database.
        Args:
            user_schema: user request schema.
            super_user_id: creator user id.
        Returns:
            User: created user.
        """
        # self.check_username_conflict(user_schema.username)
        user = User(
            username=user_schema.username,
            # created_by=super_user_id
        )
        self.session.add(user)
        self.session.commit()
        return user

    # def update_user(self, user_id: int, user_schema: UserUpdateRequest,
    #                 super_user_id: int) -> User:
    #     """Updates user by given user schema.
    #     Args:
    #         user_id: changeable user id.
    #         user_schema: user update schema.
    #         super_user_id: changer user id.
    #     Returns:
    #         User: updated user.
    #     """
    #     user = self.get_user_by_id(user_id)
    #     was_modified = False
    #     for field, value in user_schema:
    #         if value:
    #             if field == "password_text":
    #                 setattr(user, field, self.hash_password(value))
    #             else:
    #                 setattr(user, field, value)
    #             was_modified = True
    #     if was_modified:
    #         user.modified_by = super_user_id
    #     self.session.commit()
    #     return user

    def delete_user(self, user_id: int) -> None:
        """Deletes user by given id.
        Args:
            user_id: user id.
        """
        user = self.get_user_by_id(user_id)
        self.session.delete(user)
        self.session.commit()
