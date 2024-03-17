from .util import Util
from gmqtt import Client as MQTTClient
from .helper import MQPacketStatus
from .packet import MQPacket, MQPacketCovert
from .helper import Constants
from .topic_management import TopicManagement
from .packet_controller import MQTxController
from .agent_observer import MQAgentObserver
from .agent_config import MQAgentConfig
# https://github.com/wialon/gmqtt

from flat_mq_client.mqtt_factory import MqttFactory
from flat_mq_client.i_client import IMqttClient
from flat_mq_client.client_options_builder import MqttClientOptionsBuilder
from flat_mq_client.client_options import MqttClientOptions


class _MQBase:
    def __init__(self):
        pass

    async def run(self):
        self.setup()
        await self._start()

    async def release(self):
        await self._stop()

    async def _start(self):
        return NotImplementedError

    async def _stop(self):
        return NotImplementedError

    def setup(self):
        return NotImplementedError


class MQAgent(_MQBase):
    def __init__(self, observer=MQAgentObserver(), mq_config: MQAgentConfig = None):
        self._client: IMqttClient = None
        self._client_options: MqttClientOptions = None
        self._mq_config = mq_config
        self._client_id = ""
        self._role_name = ""

        self.tp_management: TopicManagement = None
        self._tx_controller: MQTxController = None
        self._observer = observer

    def setup(self) -> None:
        self.setupMQOptions()
        self._tx_controller = MQTxController()
        self.tp_management = TopicManagement()

    def setupMQOptions(self) -> MqttClientOptions:
        builder = MqttClientOptionsBuilder()
        builder.withClientID("test123_user")
        builder.withTcpServer(host=Constants().BrokerURL, port=1883)
        builder.withCleanSession()
        builder.withKeepAlive(sec=10)
        return builder.build()

    def _subscribeTopic(self):
        self._client.subscribe(self.tp_management.getSubscribe(), qos=0)

    def processContent(self, content: str) -> str:
        pass

    async def send(self, content: str) -> str:
        result: MQPacket = None
        packet = MQPacket(content=content, sender_id=self._client_id,
                          source=f"/role/{self._role_name}/{self._client_id}", status=MQPacketStatus.Rising)
        result = await self._send(packet=packet, receive_role_topic=self.tp_management.getPublish())
        if result is None:
            return result
        return result.response

    async def _send(self, packet: MQPacket, receive_role_topic: str) -> MQPacket:
        result: MQPacket = None

        try:
            if not isinstance(packet, MQPacket):
                return result

            msg = MQPacketCovert.serialize(packet=packet)

            if self._client == None:
                return result
            self._client.publish(topic=receive_role_topic, msg=msg, qos=0)
            track = self._tx_controller.requestPacket(packet=packet)
            if track == None:
                return result
            await track.startTrack()

            result = track.packet
        except:
            print("send error")

        return result

    async def _response(self, packet: MQPacket) -> None:
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
        self._client: IMqttClient = MqttFactory().createGMqttClient()
        self._client.on_msg = self.__onMessageReceived
        self._client.on_connect = self.__onConnected
        self._client.on_disconnect = self.__onDisconnected
        await self._client.startAsync(options=self._client_options)
        await self._subscribeTopic()

    async def _stop(self):
        await self._client.stopAsync()
        self._tx_controller = None

    def __onConnected(self, client, flags, rc, properties):
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
                response = self.processContent(content=packet.content)
                packet.response = response
                packet.status = MQPacketStatus.Falling

                if packet.status is MQPacketStatus.Falling:  # 處理完了，把結果送回去
                    packet.status = MQPacketStatus.Finished
                    await self._response(packet=packet)
            self._observer.onMessageReceived()
        except:
            print('receive error')

    def __onDisconnected(self, client, packet, exc=None):
        print('Disconnected')
        self._observer.onDisconnected()
