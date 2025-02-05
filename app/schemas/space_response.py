from pydantic import BaseModel
from datetime import datetime


class SpaceResponse(BaseModel):
    """Space response schema."""
    id: int
    owner_id: int
    workspace_id: int
    name: str
    num_documents: int
    last_updated: datetime

    class Config:
        orm_mode = True
        use_enum_values = True
