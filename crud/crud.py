import schema
from schema import ClientBase
from schema.client import client_to_client_base, baby_to_baby_base, ClientList
from utils import get_password_hash, verify_password
import model
import auth_schema
from model import Client, Baby
from sqlalchemy.exc import SQLAlchemyError
from functools import wraps
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func


def handle_db_exceptions(func):
    """数据库操作异常处理装饰器"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SQLAlchemyError as e:
            print(f"Database error occurred: {e}")
            return None  # 或返回适当的错误响应

    return wrapper


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


@handle_db_exceptions
def create_user(db: Session, user: auth_schema.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = model.User(
        username=user.username, email=user.email, hashed_password=hashed_password, double_check_password=user.double_check_password
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
        mode_of_delivery=client.mode_of_delivery,
        room=client.room,
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
            summary=baby.summary,
        )
        db.add(db_baby)

    db.commit()
    return get_client_and_babies(db, db_client.id)


def get_client_and_babies(db: Session, client_id: int):
    # 定义联表查询
    stmt = (
        select(Client, Baby)
        .join(Baby, Client.id == Baby.client_id)
        .where(Client.id == client_id)
    )

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
            client_response = client_to_client_base(client)

        # 向ClientBase实例的babies列表添加Baby实例
        client_response.babies.append(baby_to_baby_base(baby))

    return client_response


@handle_db_exceptions
def get_clients_and_babies_by_name(
    db: Session, client_name: Optional[str], page: int, page_size: int
) -> ClientList:
    # 计算分页的偏移量
    offset = (page - 1) * page_size

    # 定义查询基础
    base_query = select(Client, Baby).join(Baby, Client.id == Baby.client_id)

    # 如果client_name不为None，应用过滤条件
    if client_name is not None:
        base_query = base_query.where(Client.name == client_name)

    # 对查询结果进行排序
    sorted_query = base_query.order_by(Client.id)

    # 应用分页
    paginated_query = sorted_query.offset(offset).limit(page_size)

    # 执行查询，获取当前页的数据
    result = db.execute(paginated_query).fetchall()

    # 获取满足条件的总记录数
    total_records = db.execute(
        select(func.count()).select_from(sorted_query.subquery())
    ).scalar()

    # 计算总页数
    total_pages = (total_records + page_size - 1) // page_size

    clients_data = {}

    for client, baby in result:
        if client.id not in clients_data:
            clients_data[client.id] = client_to_client_base(client)
            clients_data[client.id].babies = []
        clients_data[client.id].babies.append(baby_to_baby_base(baby))

    # 构建返回的数据，包括客户数据和分页信息
    return_data = {
        "clients": list(clients_data.values()),
        "pagination": {
            "totalRecords": total_records,
            "totalPages": total_pages,
            "currentPage": page,
            "pageSize": page_size,
        },
    }

    # 返回包含客户数据和分页信息的字典
    return ClientList(**return_data)
