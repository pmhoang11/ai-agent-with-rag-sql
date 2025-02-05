from typing import Optional

from pydantic import BaseModel



class DocumentRequest(BaseModel):
    """Document request schema."""
    title: Optional[str] = None
    owner_id: int
    workspace_id: int
    space_id: int
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "owner_id": 1,
                "workspace_id": 1,
                "space_id": 1
            }
        }


class DocumentUpdateRequest(BaseModel):
    title: str | None

    class Config:
        use_enum_values = True
