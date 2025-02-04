from pydantic import BaseModel



class SpaceResponse(BaseModel):
    """Space response schema."""
    id: int
    owner_id: int
    workspace_id: int
    name: str

    class Config:
        orm_mode = True
        use_enum_values = True
