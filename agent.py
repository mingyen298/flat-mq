import asyncio
import os
import signal
import time

from .util import Util
from gmqtt import Client as MQTTClient
from .helper import MQPacketStatus
from .packet import MQPacket, MQPacketCovert
from .helper import Constants
from .topic_management import TopicManagement
from .packet_controller import MQTxController
from .agent_observer import MQAgentObserver
# https://github.com/wialon/gmqtt


class _MQBase:
    def __init__(self):
        pass

    async def run(self):
        await self._start()

    async def release(self):
        await self._stop()

    async def _start(self):
        return NotImplementedError

    async def _stop(self):
        return NotImplementedError


class MQAgent(_MQBase):
    def __init__(self, observer=MQAgentObserver()):
        self._client = None
        self.tp_management = TopicManagement()
        self._tx_controller = MQTxController()
        self._observer = observer
        

    def _subscribeTopic(self):
        self._client.subscribe(self.tp_management.getSubscribe(), qos=0)

    async def send(self, packet: MQPacket) -> MQPacket:
        result: MQPacket = None
        try:
            if not isinstance(packet, MQPacket):
                return result

            packet.status = MQPacketStatus.Rising
            msg = MQPacketCovert.serialize(packet=packet)

            if self._client == None:
                return result
            self._client.publish(self.tp_management.getPublish(),
                                 msg, qos=0)
            track = self._tx_controller.requestPacket(packet=packet)
            if track == None:
                return result
            await track.startTrack()

            result = track.packet
        except:
            print("send error")

        return result
    async def _response(self,packet:MQPacket) -> None:
        try:
            if not isinstance(packet, MQPacket):
                return None

            msg = MQPacketCovert.serialize(packet=packet)

            if self._client == None:
                return None
            self._client.publish(packet.source,
                                 msg, qos=0)

        except:
            print("send error")

    async def _start(self):
        self._client = MQTTClient("test123_user")
        self._client.on_connect = self.__onConnected
        self._client.on_message = self.__onMessageReceived
        self._client.on_disconnect = self.__onDisconnected
        await self._client.connect(Constants().BrokerURL)

    async def _stop(self):
        await self._client.disconnect()

    def __onConnected(self, client, flags, rc, properties):
        self._subscribeTopic()
        print('Connected')
        self._observer.onConnected()

    async def __onMessageReceived(self, client, topic, payload, qos, properties):

        try:
            print('RECV MSG:', payload)
            packet = MQPacketCovert.deserialize(payload)

            if packet.status is MQPacketStatus.Finished:  # response 回來的訊息
                self._tx_controller.processPacket(packet=packet)

            elif packet.status is MQPacketStatus.Rising:  # 剛送到待處理的訊息
                packet.status = MQPacketStatus.Processing
                self._observer.onMessageProcessing(content=packet.content)
                packet.status = MQPacketStatus.Falling

                if packet.status is MQPacketStatus.Falling:
                    packet.status = MQPacketStatus.Finished
                    await self._response(packet=packet)
            self._observer.onMessageReceived()
        except:
            print('receive error')

    def __onDisconnected(self, client, packet, exc=None):
        print('Disconnected')
        self._observer.onDisconnected()
