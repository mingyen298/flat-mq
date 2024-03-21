import uuid
from datetime import datetime
from .helper import MQPacketStatus
import json

class MQPacket:
    def __init__(self,
                 id=uuid.uuid4(),
                 time=int(datetime.utcnow().timestamp()),
                 content='',
                 sender_id=uuid.UUID,
                 source='',
                 response='',
                 status=MQPacketStatus.Default
                 ) -> None:
        self.id: uuid.UUID = id
        self.time: int = time
        self.content: str = content
        self.sender_id: uuid.UUID = sender_id
        self.source: str = source
        self.response: str = response
        self.status: MQPacketStatus = status

    def update(self, command):
        self.response = command.response
        self.status = command.status

    def clone(self):
        new_packet = MQPacket()
        new_packet.id = self.id
        new_packet.time = self.time
        new_packet.content = self.content
        new_packet.sender_id = self.sender_id
        new_packet.source = self.source
        new_packet.response = self.response
        new_packet.status = self.status
        return new_packet

    def __serialize__(self):
        return {
            "id": str(self.id),
            "time": self.time,
            "content": self.content,
            "sender_id": str(self.sender_id),
            "source": self.source,
            "response": self.response,
            "status": MQPacketStatus(self.status)
        }


class _MQPacketSerializer(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__serialize__'):
            return obj.__serialize__()

        return json.JSONEncoder.default(self, obj)




class MQPacketCovert:
    @staticmethod
    def serialize(packet:MQPacket) -> str:
        '''Serialize packet to string'''
        return json.dumps(packet, cls=_MQPacketSerializer)

    @staticmethod
    def deserialize(content: str) -> MQPacket:
        dict = json.loads(content)
        packet = MQPacket()
        packet.id = uuid.UUID(dict.get('id', ''))
        packet.time = dict.get('time', 0)
        packet.content = dict.get('content', '')
        packet.sender_id = dict.get('sender_id', '')
        packet.source = dict.get('source', '')
        packet.response = dict.get('response', '')
        packet.status = MQPacketStatus(dict.get('status'))
        return packet