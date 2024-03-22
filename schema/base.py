from typing import Optional

from pydantic import BaseModel


class BabyNurse(BaseModel):
    baby_nurse_id: int
    name: str
    age: str
    tel: str
    address: str
    id_number: str
    childcare_certificate: str


class BabyNurseModel(BaseModel):
    baby_nurse_id: Optional[int] = None
    name: Optional[str] = None
    age: Optional[str] = None
    tel: Optional[str] = None
    address: Optional[str] = None
    id_number: Optional[str] = None
    childcare_certificate: Optional[str] = None
