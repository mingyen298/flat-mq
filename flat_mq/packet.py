import uuid
from .helper import MQPacketStatus
from pydantic import BaseModel

class MQPacket(BaseModel):

    id: uuid.UUID 
    time: int 
    content: str = ""
    sender_id: str
    source: str = ""
    response: str = ""
    status: MQPacketStatus = MQPacketStatus.Default

    def update(self, command:'MQPacket'):
        self.response = command.response
        self.status = command.status

    def clone(self):
        new_packet = MQPacket(id=self.id,
                              time=self.time,
                              content=self.content,
                              sender_id=self.sender_id,
                              source=self.source,
                              response=self.response,
                              status=self.status)

        return new_packet

class MQPacketCovert:
    @staticmethod
    def serialize(packet:MQPacket) -> str:
        '''Serialize packet to string'''
        return MQPacket.json(packet)

    @staticmethod
    def deserialize(content: str) -> MQPacket:

        return MQPacket.parse_raw(content)