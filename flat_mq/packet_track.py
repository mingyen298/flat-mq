import asyncio
from .packet import MQPacket


class MQPacketTrack:
    def __init__(self, packet: MQPacket) -> None:
        self.__track:asyncio.Future = None
        self.__packet: MQPacket = packet

    @property
    def packet(self) -> MQPacket:
        return self.__packet

    @packet.setter
    def packet(self, value):
        if isinstance(value, MQPacket):
            self.__packet = value

    def startTrack(self) -> asyncio.Future:
        self.__track = asyncio.get_event_loop().create_future()
        return self.__track

    def finish(self, packet: MQPacket = None) -> None:
        if self.__packet != None:
            self.__packet.update(packet)
        self.__track.set_result(True)
