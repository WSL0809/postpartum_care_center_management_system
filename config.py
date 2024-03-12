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
