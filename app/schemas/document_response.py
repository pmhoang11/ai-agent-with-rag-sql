from pydantic import BaseModel
from datetime import datetime



class DocumentResponse(BaseModel):
    """Space response schema."""
    id: int
    owner_id: int
    workspace_id: int
    space_id: int
    title: str
    uploaded_date: datetime

    class Config:
        orm_mode = True
        use_enum_values = True
