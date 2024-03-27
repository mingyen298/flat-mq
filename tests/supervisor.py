import sys
sys.path.insert(0, sys.path[0]+"/../")
from flat_mq.agent_config import MQAgentConfigBuilder,MQAgentConfig

import asyncio
import signal
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


class Supervisor(MQAgent):
    def __init__(self):

        build = MQAgentConfigBuilder()
        build.withSelfAgentID(role=Role.Supervisor.name)
        build.withOtherAgentID(role=Role.Coordinator.name)
        config = build.build()
        print(config.listen_topic)
        print(config.send_topics)
        super().__init__(agent_config=config)

    async def processContent(self, content: str) -> str:
        print(content)
        return "OK"

    def sendToCoordinator(self, content: str):
        super().send(role=Role.Coordinator.name, content=content)


async def main():

    supervisor = Supervisor()
    await supervisor.run()
    # await supervisor.sendToCoordinator(content="123")

    await STOP.wait()
    await supervisor.release()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    loop.add_signal_handler(signal.SIGINT, ask_exit)
    loop.add_signal_handler(signal.SIGTERM, ask_exit)

    loop.run_until_complete(main())
