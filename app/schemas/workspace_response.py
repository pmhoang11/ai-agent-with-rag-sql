from pydantic import BaseModel
from datetime import datetime


class WorkspaceResponse(BaseModel):
    """Workspace response schema."""
    id: int
    owner_id: int
    name: str
    last_updated: datetime

    class Config:
        orm_mode = True
        use_enum_values = True
