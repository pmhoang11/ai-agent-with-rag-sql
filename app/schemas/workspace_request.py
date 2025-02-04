from pydantic import BaseModel



class WorkspaceRequest(BaseModel):
    """Workspace request schema."""
    name: str
    owner_id: int
    class Config:
        use_enum_values = True


class WorkspaceUpdateRequest(BaseModel):
    name: str | None

    class Config:
        use_enum_values = True
