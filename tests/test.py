import sys
sys.path.insert(0, sys.path[0]+"/../")
from flat_mq.packet import MQPacket
import uuid
from datetime import datetime
# class PacketBase(BaseModel):

#     def __init__(self,id,time,status):
#         id: uuid.UUID = uuid.uuid4()
#         time: datetime
#         status:MQPacketStatus

# class Command(PacketBase):
#     content: str



p = MQPacket(id=uuid.uuid4(),time=int(datetime.utcnow().timestamp()),sender_id=uuid.uuid4())
print(p)
p2 = p.clone()
print(p2)

# 序列化
# command = Command( time=datetime.now(), content="Example command",status=MQPacketStatus.Default)
# json_str = command.json()
# print(json_str)
# command = Command( time=datetime.now(), content="Example command",status=MQPacketStatus.Default)
# json_str = command.json()
# print(json_str)
# 反序列化
# decoded_command = Command.parse_raw(json_str)
# print(decoded_command.id)



