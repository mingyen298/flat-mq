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
from .packet_controller import MQTxPacketController

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
    def __init__(self):
        self.client = None
        self.tp_management = TopicManagement()
        self.tx_controller = MQTxPacketController()
        # 讓使用者自訂事件的callback
        self.on_connect = None
        self.on_message = None
        self.on_disconnect = None

    def _subscribeTopic(self):
        self.client.subscribe(self.tp_management.getSubscribe(), qos=0)

    async def send(self, packet: MQPacket) -> MQPacket:
        result = None
        try:
            if not isinstance(packet, MQPacket):
                return result
            # if not Util.isValidUUID(packet.sender_id):
            #     return
            msg = MQPacketCovert.serialize(packet=packet)

            if self.client == None :
                return result
            self.client.publish(self.tp_management.getPublish(),
                                    msg, qos=0)
            track = self.tx_controller.requestPacket(packet=packet)
            if track == None:
                return result
            await track.startTrack()

            result = track.packet
        except:
            print("send error")

        return result




    # def response(self):#要考慮放到mq_switch去做 畢竟他會封裝send跟等待response的功能，還有最接收封包
    #     self.client.publish(self.tp_management.getResponse(),
    #                         str(time.time()), qos=0)

    async def _start(self):
        self.client = MQTTClient("test123_user")
        self.client.on_connect = self.__onConnected
        self.client.on_message = self.__onMessageReceived
        self.client.on_disconnect = self.__onDisconnected
        await self.client.connect(Constants().BrokerURL)

    async def _stop(self):
        await self.client.disconnect()

    def __onConnected(self, client, flags, rc, properties):
        self._subscribeTopic()
        print('Connected')
        if self.on_connect != None:
            self.on_connect()

    def __onMessageReceived(self, client, topic, payload, qos, properties):
       
        try:
            print('RECV MSG:', payload)
            packet = MQPacketCovert.deserialize(payload)

            if packet.status == MQPacketStatus.Sending:
                pass
            if self.on_message != None:
                self.on_message()
        except:
            print('receive error')


    def __onDisconnected(self, client, packet, exc=None):
        print('Disconnected')
        if self.on_disconnect != None:
            self.on_disconnect()
