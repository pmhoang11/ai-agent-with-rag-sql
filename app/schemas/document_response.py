from pydantic import BaseModel



class DocumentResponse(BaseModel):
    """Space response schema."""
    id: int
    owner_id: int
    workspace_id: int
    space_id: int
    title: str

    class Config:
        orm_mode = True
        use_enum_values = True
