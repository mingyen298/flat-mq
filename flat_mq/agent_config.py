import json
from typing import overload


class MQAgentConfig:
    def __init__(self) -> None:
        self.agent_id: str = ""
        self.listen_topic: str = ""
        self.send_topics: dict = dict()
        self.host: str = "0.0.0.0"
        self.port:int = 1883


class MQAgentConfigBuilder:
    def __init__(self) -> None:
        self._config = MQAgentConfig()
        self._id = ""
        self._role = ""
        self._other_roles = dict()

    def withSelfAgentID(self, role: str, id: str = "") -> None:
        self._role = role
        self._id = id

    def withOtherAgentID(self, role: str, id: str = "") -> None:
        if id == "":
            self._other_roles[role] = f'role/{role}'
        else:
            self._other_roles[role] = f'role/{role}/{id}'

    def withTcpServer(self,host:str , port:int)->None:
        self._config.host = host
        self._config.port = port

    def build(self):

        if self._id == "":
            self._config.agent_id = f'{self._role}'
            self._config.listen_topic = f'role/{self._role}'
        else:
            self._config.agent_id = f'{self._role}-{self._id}'
            self._config.listen_topic = f'role/{self._role}/{self._id}'

        for role, topic in self._other_roles.items():
            self._config.send_topics[role] = topic

        return self._config


