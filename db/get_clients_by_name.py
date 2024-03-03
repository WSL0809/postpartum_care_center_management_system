from sqlalchemy import text
from sqlalchemy.orm import Session
from pydantic import BaseModel, date
from typing import List, Tuple


class ClientBase(BaseModel):
    id: int
    name: str
    tel: str
    age: int
    scheduled_date: date
    check_in_date: date
    hospital_for_childbirth: str
    contact_name: str
    contact_tel: str
    summary: str
    babies: str
    meal_plan: str
    recovery_plan: str


class ClientList(BaseModel):
    clients: List[ClientBase]
    total: int


# 保持 ClientBase 和 ClientList 定义不变


def get_clients_by_name(
    db: Session, name: str, page: int, page_size: int
) -> ClientList:
    """
    使用 SQL 语句根据名字分页查询客户信息，并使用 Pydantic 校验。

    :param name: 客户名字
    :param page: 页码，从1开始
    :param page_size: 每页大小
    :return: ClientList 实例（包含客户列表和总数）
    """
    # 计算跳过的记录数
    offset = (page - 1) * page_size

    # 准备 SQL 语句
    total_sql = text("SELECT COUNT(*) FROM client WHERE name = :name")
    clients_sql = text("""
        SELECT * FROM client
        WHERE name = :name
        ORDER BY id
        LIMIT :limit OFFSET :offset
    """)

    # 执行查询
    total = db.execute(total_sql, {"name": name}).scalar()
    clients_result = db.execute(
        clients_sql, {"name": name, "limit": page_size, "offset": offset}
    ).fetchall()

    # 使用 Pydantic 校验并构造客户列表
    clients = [
        ClientBase(
            id=client["id"],
            name=client["name"],
            tel=client["tel"],
            age=client["age"],
            scheduled_date=client["scheduled_date"],
            check_in_date=client["check_in_date"],
            hospital_for_childbirth=client["hospital_for_childbirth"],
            contact_name=client["contact_name"],
            contact_tel=client["contact_tel"],
            summary=client["summary"],
            # 注意：这里的 babies, meal_plan, recovery_plan 应根据实际返回数据调整
            babies="",
            meal_plan="",
            recovery_plan="",
        )
        for client in clients_result
    ]

    # 返回客户列表和总数
    return ClientList(clients=clients, total=total)
