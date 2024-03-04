from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

import schema
from schema import ClientBase, ClientCreate
from utils import get_password_hash, verify_password
import model
import schemas
from model import Client, Baby
from sqlalchemy.exc import NoResultFound
from typing import Tuple, List


def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def get_user(db: Session, user_name: str):
    return db.query(model.User).filter(model.User.username == user_name).first()


def is_user_exits(db: Session, user_name: str):
    if db.query(model.User).filter(model.User.username == user_name).first():
        return True
    else:
        return False


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = model.User(
        username=user.username, email=user.email, hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_client(db: Session, client: schema.ClientCreate):
    db_client = model.Client(
        meal_plan_id=client.meal_plan_id,
        recovery_plan_id=client.recovery_plan_id,
        assigned_baby_nurse=client.assigned_baby_nurse,
        name=client.name,
        tel=client.tel,
        age=client.age,
        scheduled_date=client.scheduled_date,
        check_in_date=client.check_in_date,
        hospital_for_childbirth=client.hospital_for_childbirth,
        contact_name=client.contact_name,
        contact_tel=client.contact_tel,
        mode_of_delivery=client.mode_of_delivery
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    for baby in client.babies:
        db_baby = model.Baby(
            client_id=db_client.id,
            name=baby.name,
            gender=baby.gender,
            birth_date=baby.birth_date,
            birth_weight=baby.birth_weight,
            birth_height=baby.birth_height,
            health_status=baby.health_status,
            birth_certificate=baby.birth_certificate,
            remarks=baby.remarks,
            mom_id_number=baby.mom_id_number,
            dad_id_number=baby.dad_id_number,
            summary=baby.summary

        )
        db.add(db_baby)

    db.commit()
    return get_client_and_babies(db, db_client.id)


# def get_client_and_babies(db: Session, client_id: int):
#     # 定义联表查询
#     stmt = select(Client, Baby).join(Baby, Client.id == Baby.client_id).where(Client.id == client_id)
#
#     # 执行查询
#     result = db.execute(stmt)
#
#     # 处理结果
#     client_babies_data = result.fetchall()
#     clients_dict = {}
#     client_response = ClientBase()
#     # 遍历查询结果
#     for row in client_babies_data:
#         # 假设每个行的结构是 (Client, Baby)
#         client, baby = row
#
#         # 检查客户是否已经在字典中
#         if client.id not in clients_dict:
#             # 如果不在，添加客户信息和一个空的宝宝列表
#             clients_dict[client.id] = {
#                 "client_info": {
#                     "name": client.name,
#                     "tel": client.tel,
#                     # 添加更多需要的客户信息...
#                 },
#                 "babies": []
#             }
#
#         # 向客户的宝宝列表添加宝宝信息
#         clients_dict[client.id]["babies"].append({
#             "name": baby.name,
#             "birth_date": baby.birth_date,
#             # 添加更多需要的宝宝信息...
#         })
#
#     print(clients_dict)

def get_client_and_babies(db: Session, client_id: int):
    # 定义联表查询
    stmt = select(Client, Baby).join(Baby, Client.id == Baby.client_id).where(Client.id == client_id)

    # 执行查询
    result = db.execute(stmt)

    # 处理结果
    client_babies_data = result.fetchall()
    # 假设我们只处理一个客户（因为我们通过客户ID查询）
    client_response = None

    # 遍历查询结果
    for row in client_babies_data:
        client, baby = row  # 假设每行结构是 (Client, Baby)
        if client_response is None:
            # 初始化ClientBase实例
            client_response = ClientBase(
                name=client.name,
                tel=client.tel,
                age=client.age,  # 假设这些字段存在
                scheduled_date=client.scheduled_date,
                check_in_date=client.check_in_date,
                hospital_for_childbirth=client.hospital_for_childbirth,
                contact_name=client.contact_name,
                contact_tel=client.contact_tel,
                babies=[],
                meal_plan=client.meal_plan_id,
                recovery_plan=client.recovery_plan_id,
                mode_of_delivery=client.mode_of_delivery,
                assigned_baby_nurse=client.assigned_baby_nurse
            )

        # 向ClientBase实例的babies列表添加Baby实例
        client_response.babies.append(Baby(
            name=baby.name,
            gender=baby.gender,
            birth_date=baby.birth_date,
            birth_weight=baby.birth_weight,
            birth_height=baby.birth_height,
            health_status=baby.health_status,
            birth_certificate=baby.birth_certificate,
            remarks=baby.remarks,
            mom_id_number=baby.mom_id_number,
            dad_id_number=baby.dad_id_number,
            summary=baby.summary))

    return client_response

def get_clients_by_name(
        db: Session, name: str, page: int, page_size: int
) -> Tuple[List[Client], int]:
    """
    根据名字分页查询客户信息。

    :param name: 客户名字
    :param page: 页码，从1开始
    :param page_size: 每页大小
    :return: (客户列表, 总客户数)
    """
    try:
        # 计算跳过的记录数
        offset = (page - 1) * page_size

        # 查询总数
        total = db.query(Client).filter(Client.name == name).count()

        # 分页查询
        clients = (
            db.query(Client)
            .filter(Client.name == name)
            .order_by(Client.id)
            .offset(offset)
            .limit(page_size)
            .options(
                joinedload(Client.babies),
                joinedload(Client.meal_plan),
                joinedload(Client.recovery_plan),
            )
            .all()
        )

        return clients, total
    except NoResultFound:
        return [], 0
    finally:
        db.close()
