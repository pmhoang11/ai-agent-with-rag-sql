from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status

from app.db.base import get_session
from app.models.workspace import Workspace
from app.schemas.workspace_request import WorkspaceRequest, WorkspaceUpdateRequest



class WorkspacesService:
    """Workspaces service for interacting with the database."""

    def __init__(self) -> None:
        self.session = next(get_session())

    def __del__(self):
        self.session.close()  # Ensure the session is closed when the object is destroyed

    def get_all_workspaces(self) -> list[Workspace]:
        """Returns all workspaces.
        Returns:
            list[Workspace]: list of workspaces.
        """
        workspaces = (
            self.session
            .query(Workspace)
            .order_by(Workspace.id.desc())
            .all()
        )
        return workspaces

    def get_workspace_by_id(self, workspace_id: int) -> Workspace:
        """Finds workspace by given workspace_id.
        Args:
            workspace_id: workspace_id id.
        Returns:
            workspace: found workspace.
        """
        workspace = (
            self.session
            .query(Workspace)
            .filter(Workspace.id == workspace_id)
            .first()
        )
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        return workspace

    def get_workspace_by_name(self, workspace_name: str) -> Workspace:
        """Finds workspace by given workspace_name.
        Args:
            workspace_name: workspace_name.
        Returns:
            workspace: found workspace.
        """
        workspace = (
            self.session
            .query(Workspace)
            .filter(Workspace.name == workspace_name)
            .first()
        )
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        return workspace

    def add_workspace(self, workspace_schema: WorkspaceRequest) -> Workspace:
        """Creates workspace by given workspace schema and saves it in database.
        Args:
            workspace_schema: workspace request schema.
        Returns:
            workspace: found workspace.
        """
        workspace = Workspace(
            name=workspace_schema.name,
            owner_id=workspace_schema.owner_id,
        )
        self.session.add(workspace)
        self.session.commit()
        return workspace

    def update_workspace(self, workspace_id: int, workspace_schema: WorkspaceUpdateRequest) -> Workspace:
        """Updates workspace by given workspace schema.
        Args:
            workspace_id: changeable workspace id.
            workspace_schema: workspace update schema.
        Returns:
            workspace: updated workspace.
        """
        workspace = self.get_workspace_by_id(workspace_id)

        for field, value in workspace_schema:
            if value:
                setattr(workspace, field, value)

        self.session.commit()
        return workspace

    def increase_num_spaces(self, workspace_id: int) -> Workspace:
        """Updates workspace by given workspace schema.
        Args:
            workspace_id: changeable workspace id.
        Returns:
            workspace: updated workspace.
        """
        workspace = self.get_workspace_by_id(workspace_id)
        workspace.num_spaces += 1
        self.session.commit()
        return workspace

    def delete_workspace(self, workspace_id: int) -> None:
        """Deletes workspace by given id.
        Args:
            workspace_id: workspace_id.
        """
        workspace = self.get_workspace_by_id(workspace_id)
        self.session.delete(workspace)
        self.session.commit()
