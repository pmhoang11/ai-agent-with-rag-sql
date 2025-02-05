from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status

from app.db.base import get_session
from app.models.space import Space
from app.schemas.space_request import SpaceRequest, SpaceUpdateRequest



class SpacesService:
    """Spaces service for interacting with the database."""

    def __init__(self) -> None:
        self.session = next(get_session())

    def __del__(self):
        self.session.close()  # Ensure the session is closed when the object is destroyed

    def get_all_spaces(self) -> list[Space]:
        """Returns all spaces.
        Returns:
            list[Space]: list of spaces.
        """
        spaces = (
            self.session
            .query(Space)
            .order_by(Space.id.desc())
            .all()
        )
        return spaces

    def get_space_by_id(self, space_id: int) -> Space:
        """Finds space by given space_id.
        Args:
            space_id: space_id id.
        Returns:
            space: found space.
        """
        space = (
            self.session
            .query(Space)
            .filter(Space.id == space_id)
            .first()
        )
        if not space:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Space not found"
            )
        return space

    def get_space_by_name(self, space_name: str) -> Space:
        """Finds space by given space_name.
        Args:
            space_name: space_name.
        Returns:
            space: found space.
        """
        space = (
            self.session
            .query(Space)
            .filter(Space.name == space_name)
            .first()
        )
        if not space:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Space not found"
            )
        return space

    def add_space(self, space_schema: SpaceRequest) -> Space:
        """Creates space by given space schema and saves it in database.
        Args:
            space_schema: space request schema.
        Returns:
            space: found space.
        """
        space = Space(
            name=space_schema.name,
            owner_id=space_schema.owner_id,
            workspace_id=space_schema.workspace_id,
        )
        self.session.add(space)
        self.session.commit()
        return space

    def update_space(self, space_id: int, space_schema: SpaceUpdateRequest) -> Space:
        """Updates space by given space schema.
        Args:
            space_id: changeable space id.
            space_schema: space update schema.
        Returns:
            space: updated space.
        """
        space = self.get_space_by_id(space_id)

        for field, value in space_schema:
            if value:
                setattr(space, field, value)

        self.session.commit()
        return space

    def delete_space(self, space_id: int) -> None:
        """Deletes space by given id.
        Args:
            space_id: space_id.
        """
        space = self.get_space_by_id(space_id)
        self.session.delete(space)
        self.session.commit()
