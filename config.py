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
    # 已入住
    in_there = 0
    # 出院
    out = 1
    # 手动创建
    manual_create = 2


class BabyNurseWorkStatus(Enum):
    # 工作中
    working = '1'
    # 待命
    standby = '0'
    # 休息
    rest = '2'
