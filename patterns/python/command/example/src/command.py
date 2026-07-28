from abc import ABC, abstractmethod


class Command(ABC):
    @abstractmethod
    def execute(self) -> None:
        ...


class Receiver:
    def action(self) -> None:
        print("Receiver.action executado")


class ConcreteCommand(Command):
    def __init__(self, receiver: Receiver) -> None:
        self._receiver = receiver

    def execute(self) -> None:
        self._receiver.action()


class Invoker:
    def __init__(self) -> None:
        self._command: Command | None = None

    def set_command(self, command: Command) -> None:
        self._command = command

    def execute_command(self) -> None:
        if self._command is not None:
            self._command.execute()
