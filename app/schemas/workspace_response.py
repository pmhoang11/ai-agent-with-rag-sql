from pydantic import BaseModel



class WorkspaceResponse(BaseModel):
    """Workspace response schema."""
    id: int
    owner_id: int
    workspace_id: int
    name: str
    num_documents: int

    class Config:
        orm_mode = True
        use_enum_values = True
