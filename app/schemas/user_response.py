from pydantic import BaseModel



class UserResponse(BaseModel):
    """User response schema."""
    id: int
    username: str

    class Config:
        orm_mode = True
        use_enum_values = True
