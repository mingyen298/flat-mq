import sys
sys.path.insert(0, sys.path[0]+"/../")

from flat_mq.agent_config import MQAgentConfigBuilder, MQAgentConfig
import uvloop
from pydantic import BaseModel
from flat_mq.packet import MQPacket
from flat_mq.agent import MQAgent
from enum import Enum, auto
import signal
import asyncio
from typing import Any



# gmqtt also compatibility with uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

STOP = asyncio.Event()


def ask_exit(*args):
    STOP.set()


class Role(str, Enum):
    Coordinator = auto()
    Supervisor = auto()
    Worker = auto()


class CommandResult( int,Enum):
    Default = auto()
    Success = auto()
    Fail = auto()
    Error = auto()


class CommandType(int,Enum):
    Default = auto()
    Apply = auto()
    Data = auto()


class Command(BaseModel):

    type: CommandType = CommandType.Default
    result: CommandResult = CommandResult.Default
    msg: str = ""
    content: str = ""

    def update(self, result=CommandResult.Success, msg="Success"):
        self.result = result
        self.msg = msg


class Supervisor(MQAgent):
    def __init__(self):

        build = MQAgentConfigBuilder()
        build.withSelfAgentID(role=Role.Supervisor.name)
        build.withOtherAgentID(role=Role.Coordinator.name)
        config = build.build()
        print(config.listen_topic)
        print(config.send_topics)
        super().__init__(agent_config=config)

    async def processPacket(self, packet: MQPacket) -> Any:
        resp: Command = None
        command = Command.parse_raw(packet.content)

        if command.type == CommandType.Apply:
            command.update()

        elif command.type == CommandType.Data:
            command.update(msg="QAQ")
        else:
            command.update(result=CommandResult.Fail, msg="Fail")

        resp = command
        return resp

    async def sendToCoordinator(self, content: str) -> Command:
        command = Command(type=CommandType.Data,
                          result=CommandResult.Default,
                          content=content)
        return await self.send(role=Role.Coordinator.name,
                               content_obj=command,
                               cls=Command)


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
