import json
from typing import List

from sqlalchemy import select, text
from sqlalchemy.orm import Session

import crud
import model
import schema
from model import Room, Client
from model.client import MealPlan, RecoveryPlan
from schema.base import BabyNurse, BabyNurseModel
from schema.client import ClientModel, ClientCreate
from schema.plan import MealPlanModel, RecoveryPlanModel
from schema.room import RoomModel, RoomClientModel


def get_all_rooms(db: Session):
    return db.query(model.Room).all()


def get_room_by_id(db: Session, room_id: int):
    query = select(
        model.Room.id, model.Room.status, model.Room.recently_used, model.Room.notes
    ).where(model.Room.id == room_id)
    res = db.execute(query).first()
    if res is not None:
        id, status, recently_used, notes = db.execute(query).first()
    else:
        id, status, recently_used, notes = (-1, "None", "None", "None")
    return schema.Room(id=id, status=status, recently_used=recently_used, notes=notes)


def get_room_by_room_number(db: Session, room_number: str):
    query = select(model.Room).where(model.Room.room_number == room_number)
    res = db.execute(query).first()
    if res is not None:
        id, status, recently_used, notes = db.execute(query).first()
    else:
        id, status, recently_used, notes = (-1, "None", "None", "None")
    return schema.Room(id=id, status=status, recently_used=recently_used, notes=notes)


def get_all_room_info(db: Session):
    sql = text(
        """
        SELECT *
        FROM room
        JOIN client ON room.client_id = client.id
        LEFT JOIN meal_plan ON client.meal_plan_id = meal_plan.meal_plan_id
        LEFT JOIN recovery_plan ON client.recovery_plan_id = recovery_plan.recovery_plan_id
        LEFT JOIN baby_nurse ON client.assigned_baby_nurse = baby_nurse.baby_nurse_id
        """
    )
    res = db.execute(sql).fetchall()
    return json.dumps([row._asdict() for row in res])


def change_room_status(db: Session, room_number: str, status: str):
    db.query(Room).filter(Room.room_number == room_number).update({Room.status: status})
    db.commit()

    return


def set_room_client(db: Session, client: RoomClientModel):
    set_status = client.set_status
    with db.begin():  # 开启一个事务块
        # 创建客户端条目
        exists = (
            db.query(model.Room).filter(model.Room.room_number == client.room).first()
            is not None
        )

        if not exists:
            return {"status": "fail", "details": "room does not exist"}
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
        db.add(db_client)  # 将客户端条目添加到会话中，准备提交

    with db.begin():
        # 循环添加所有相关的婴儿信息
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
            db.add(db_baby)  # 将婴儿条目添加到会话中

        # 更新房间状态
        # 先检查是否存在匹配的记录
        exists = (
            db.query(model.Room).filter(model.Room.room_number == client.room).first()
            is not None
        )

        if not exists:
            return {"status": "fail", "details": "room does not exist"}
        else:
            # 更新状态
            db.query(model.Room).filter(model.Room.room_number == client.room).update(
                {model.Room.status: set_status}, synchronize_session=False
            )

            # 更新客户ID
            db.query(model.Room).filter(model.Room.room_number == client.room).update(
                {model.Room.client_id: db_client.id}, synchronize_session=False
            )

    return {"status": "success", "details": "success"}
