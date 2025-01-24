from pydantic import BaseModel



class UserRequest(BaseModel):
    """User request schema."""
    username: str

    class Config:
        use_enum_values = True


class UserUpdateRequest(BaseModel):
    username: str | None

    class Config:
        use_enum_values = True
