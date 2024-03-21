from enum import Enum, auto


class MiddlewareResult(int, Enum):
    Default = 0
    Success = auto()
    Fail = auto()


class MQMiddleWare:
    def handle(self, context: dict) -> MiddlewareResult:
        return NotImplementedError


class Chain:
    def __init__(self):
        self._middlewares = list[MQMiddleWare]()

    def addMiddleware(self, middleware: MQMiddleWare):
        self._middlewares.append(middleware)

    def handle(self, context: dict):
        for middleware in self._middlewares:
            result = middleware.handle(context=context)
            if result is MiddlewareResult.Fail:
                print("Request processing stopped.")
                break


class AMiddleware(MQMiddleWare):
    def handle(self, context: dict) -> MiddlewareResult:
        return MiddlewareResult.Success

    def authenticate(self, context: dict) -> bool:
        """Implement authentication logic here."""
        # Return True if authentication is successful, else False.
        pass
