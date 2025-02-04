from app.db.workspace import WorkspacesService
from fastapi import APIRouter, Depends, status

from app.schemas.workspace_request import WorkspaceRequest
from app.schemas.workspace_response import WorkspaceResponse

router = APIRouter(
    prefix='/workspaces',
    tags=['Workspaces'],
)


@router.post(
    '/create',
    response_model=WorkspaceResponse,
    status_code=status.HTTP_201_CREATED,
    name='User creation'
)
def create_workspace(
    workspace_schema: WorkspaceRequest,
    workspace_service: WorkspacesService = Depends(),
):
    return workspace_service.add_workspace(workspace_schema)


@router.get(
    '/all',
    response_model=list[WorkspaceResponse],
    status_code=status.HTTP_200_OK,
    name='Get all workspaces'
)
def get_all_workspaces(
        workspace_service: WorkspacesService = Depends()
):
    return workspace_service.get_all_workspaces()
