from app.db.space import SpacesService
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
):
    return space_service.add_space(space_schema)


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
