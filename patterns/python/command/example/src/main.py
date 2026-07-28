from command import Command, Invoker


class Light:
    def turn_on(self) -> None:
        print("Luz ligada")

    def turn_off(self) -> None:
        print("Luz desligada")


class LightOnCommand(Command):
    def __init__(self, light: Light) -> None:
        self._light = light

    def execute(self) -> None:
        self._light.turn_on()


class LightOffCommand(Command):
    def __init__(self, light: Light) -> None:
        self._light = light

    def execute(self) -> None:
        self._light.turn_off()


def main() -> None:
    light = Light()
    invoker = Invoker()

    invoker.set_command(LightOnCommand(light))
    invoker.execute_command()

    invoker.set_command(LightOffCommand(light))
    invoker.execute_command()


if __name__ == "__main__":
    main()
