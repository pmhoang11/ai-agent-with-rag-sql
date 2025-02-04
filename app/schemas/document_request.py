from pydantic import BaseModel



class DocumentRequest(BaseModel):
    """Document request schema."""
    title: str
    owner_id: int
    workspace_id: int
    space_id: int
    class Config:
        use_enum_values = True


class DocumentUpdateRequest(BaseModel):
    title: str | None

    class Config:
        use_enum_values = True
