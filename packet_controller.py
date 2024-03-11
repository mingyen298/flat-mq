from threading import Lock
import uuid

from communicator.packet import MQPacket
from .packet_track import MQPacketTrack
from .packet import MQPacket, MQPacketCovert
from .helper import MQPacketStatus


class MQSwitchBase:
    def __init__(self) -> None:
        pass

    def processPacket(self, content: str) -> MQPacket:
        packet = MQPacketCovert.deserialize(content=content)
        return self._processCommand(packet=packet)


class MQTxPacketController:
    def __init__(self) -> None:
        self.__lock: Lock = Lock()
        self.__map: dict[uuid.UUID, MQPacketTrack] = dict[uuid.UUID, MQPacketTrack]()

    def requestPacket(self, packet: MQPacket) -> MQPacketTrack:
        with self.__lock:
            # 若原本存在就把這個track砍掉
            if packet.id in self.__map:
                self.__map.get(packet.id).finish()
                del self.__map[packet.id]
            # 使用這個track跑
            if not packet.id in self.__map:
                self.__map[packet.id] = MQPacketTrack()
                return self.__map.get(packet.id)
        return None

    def receivePacket(self, packet: MQPacket) -> MQPacket:
        with self.__lock:
            if packet.status == MQPacketStatus.Responding:
                if packet.id in self.__map:
                    track = self.__map.get(packet.id)
                    track.finish(packet=packet)
                    del self.__map[packet.id]
