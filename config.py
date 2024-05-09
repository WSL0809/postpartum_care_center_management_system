from enum import Enum


class RoomStatus(Enum):
    # 空闲的房间
    Free = "0"
    # 被占用的房间
    Occupied = "2"
    # 维修的房间
    Repair = "3"
    # 已预约的房间
    Booked = "1"


class ClientStatus(Enum):
    # 直接从房态管理里添加的顾客（房态显示已预定） *vip客户*
    in_there = 0
    # 住完已经离开月子中心的顾客
    out = 1
    # 手动创建
    manual_create_without_room = 2


class BabyNurseWorkStatus(Enum):
    # 工作中
    working = '1'
    # 待命
    standby = '0'
    # 休息
    rest = '2'
