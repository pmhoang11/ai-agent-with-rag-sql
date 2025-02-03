from app.db.user import UsersService
from fastapi import APIRouter, Depends, status

from app.schemas.user_request import UserRequest
from app.schemas.user_response import UserResponse

router = APIRouter(
    prefix='/users',
    tags=['Users'],
)


@router.post(
    '/create',
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    name='User creation'
)
def create_user(
    user_schema: UserRequest,
    user_service: UsersService = Depends(),
):
    return user_service.add_user(user_schema)


@router.get(
    '/all',
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
    name='Get all users'
)
def get_all_users(
        user_service: UsersService = Depends()
):
    return user_service.get_all_users()
