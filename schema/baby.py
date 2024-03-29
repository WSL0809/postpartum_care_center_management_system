from typing import Optional

from pydantic import BaseModel


class Baby(BaseModel):
    # client_id: int
    name: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    birth_weight: Optional[str] = None
    birth_height: Optional[str] = None
    health_status: Optional[str] = None
    birth_certificate: Optional[str] = None
    remarks: Optional[str] = None
    mom_id_number: Optional[str] = None
    dad_id_number: Optional[str] = None
    summary: Optional[str] = None

    class Config:
        orm_mode = True
