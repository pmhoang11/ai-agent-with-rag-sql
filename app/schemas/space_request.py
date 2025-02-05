from pydantic import BaseModel



class SpaceRequest(BaseModel):
    """Space request schema."""
    name: str
    owner_id: int
    workspace_id: int
    class Config:
        use_enum_values = True


class SpaceUpdateRequest(BaseModel):
    name: str | None
    num_documents: int

    class Config:
        use_enum_values = True
