from app.db.space import SpacesService
from app.db.workspace import WorkspacesService
from fastapi import APIRouter, Depends, status

from app.schemas.space_request import SpaceRequest
from app.schemas.space_response import SpaceResponse

router = APIRouter(
    prefix='/spaces',
    tags=['Spaces'],
)


@router.post(
    '/create',
    response_model=SpaceResponse,
    status_code=status.HTTP_201_CREATED,
    name='User creation'
)
def create_space(
    space_schema: SpaceRequest,
    space_service: SpacesService = Depends(),
    workspace_service: WorkspacesService = Depends(),
):
    space = space_service.add_space(space_schema)
    workspace_service.increase_num_spaces(space.workspace_id)
    return space


@router.get(
    '/all',
    response_model=list[SpaceResponse],
    status_code=status.HTTP_200_OK,
    name='Get all spaces'
)
def get_all_spaces(
        space_service: SpacesService = Depends()
):
    return space_service.get_all_spaces()


@router.get(
    '/all-in-workspace',
    response_model=list[SpaceResponse],
    status_code=status.HTTP_200_OK,
    name='Get all spaces in workspace'
)
def get_all_spaces_in_workspace(
        workspace_id: int,
        space_service: SpacesService = Depends(),
):
    return space_service.get_all_spaces_in_workspace(workspace_id)