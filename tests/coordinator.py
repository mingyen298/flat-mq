from flat_mq.agent_config import MQAgentConfigBuilder
from flat_mq.helper import MQPacketStatus
from flat_mq.packet import MQPacket
import uuid
import asyncio
import os
import signal
import time
from enum import Enum, auto

from flat_mq.agent import MQAgent
# gmqtt also compatibility with uvloop
import uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

STOP = asyncio.Event()


def ask_exit(*args):
    STOP.set()


class Role(str, Enum):
    Coordinator = auto()
    Supervisor = auto()
    Worker = auto()


class Coordinator(MQAgent):
    def __init__(self):

        build = MQAgentConfigBuilder()
        build.withSelfAgentID(role=Role.Coordinator.name)
        build.withOtherAgentID(role=Role.Supervisor.name)
        config = build.build()
        print(config.listen_topic)
        print(config.send_topics)
        super().__init__(agent_config=config)

    def processContent(self, content: str) -> str:
        print(content)
        return "OK"

    async def sendToSupervisor(self, content: str):
        await self.send(role=Role.Supervisor.name, content=content)


async def main():

    coordinator = Coordinator()
    await coordinator.run()
    print("started")
    await coordinator.sendToSupervisor(content="123")

    await STOP.wait()
    await coordinator.release()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    loop.add_signal_handler(signal.SIGINT, ask_exit)
    loop.add_signal_handler(signal.SIGTERM, ask_exit)

    loop.run_until_complete(main())
