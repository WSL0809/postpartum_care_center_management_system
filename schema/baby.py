from pydantic import BaseModel


class Baby(BaseModel):
    # client_id: int
    name: str
    gender: str
    birth_date: str
    birth_weight: str
    birth_height: str
    health_status: str
    birth_certificate: str
    remarks: str
    mom_id_number: str
    dad_id_number: str
    summary: str

    class Config:
        orm_mode = True
