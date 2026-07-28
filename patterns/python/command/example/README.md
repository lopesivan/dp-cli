Aqui está um exemplo completo de como usar essa classe Command:

```python
# Exemplo de uso do padrão Command

# 1. Criar o Receiver (quem executa a ação)
receiver = Receiver()

# 2. Criar o ConcreteCommand (comando concreto)
command = ConcreteCommand(receiver)

# 3. Criar o Invoker (quem dispara o comando)
invoker = Invoker()

# 4. Configurar o comando no invoker
invoker.set_command(command)

# 5. Executar o comando
invoker.execute_command()  # Saída: Receiver.action executado
```

## Exemplos mais elaborados:

### Exemplo 1: Múltiplos comandos

```python
# Comandos com diferentes receivers
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

# Uso
light = Light()
invoker = Invoker()

# Ligar a luz
invoker.set_command(LightOnCommand(light))
invoker.execute_command()  # Saída: Luz ligada

# Desligar a luz
invoker.set_command(LightOffCommand(light))
invoker.execute_command()  # Saída: Luz desligada
```

### Exemplo 2: Macro com múltiplos comandos

```python
class MacroCommand(Command):
    def __init__(self, commands: list[Command]) -> None:
        self._commands = commands

    def execute(self) -> None:
        for command in self._commands:
            command.execute()

# Uso com múltiplos comandos
light = Light()
receiver = Receiver()

light_on = LightOnCommand(light)
light_off = LightOffCommand(light)
receiver_command = ConcreteCommand(receiver)

# Criar macro que executa vários comandos em sequência
macro = MacroCommand([
    light_on,
    receiver_command,
    light_off
])

invoker.set_command(macro)
invoker.execute_command()
# Saída:
# Luz ligada
# Receiver.action executado
# Luz desligada
```

### Exemplo 3: Comando com undo (desfazer)

```python
class CommandWithUndo(ABC):
    @abstractmethod
    def execute(self) -> None:
        ...

    @abstractmethod
    def undo(self) -> None:
        ...

class TextEditor:
    def __init__(self) -> None:
        self._text = ""

    def append(self, text: str) -> None:
        self._text += text

    def delete_last(self, count: int) -> None:
        self._text = self._text[:-count]

    def get_text(self) -> str:
        return self._text

class AppendCommand(CommandWithUndo):
    def __init__(self, editor: TextEditor, text: str) -> None:
        self._editor = editor
        self._text = text
        self._previous_state = ""

    def execute(self) -> None:
        self._previous_state = self._editor.get_text()
        self._editor.append(self._text)

    def undo(self) -> None:
        # Restaurar estado anterior (simplificado)
        self._editor._text = self._previous_state

# Uso com undo
editor = TextEditor()
append_cmd = AppendCommand(editor, "Hello")
invoker = Invoker()

invoker.set_command(append_cmd)
invoker.execute_command()
print(editor.get_text())  # Saída: Hello

# Para desfazer, você precisaria de um histórico
# append_cmd.undo()
# print(editor.get_text())  # Saída: (vazio)
```

### Exemplo 4: Filas de comandos

```python
import time
from typing import List

class CommandQueue:
    def __init__(self) -> None:
        self._queue: List[Command] = []

    def add_command(self, command: Command) -> None:
        self._queue.append(command)

    def process_commands(self) -> None:
        for command in self._queue:
            command.execute()
            time.sleep(0.5)  # Simular processamento
        self._queue.clear()

# Uso com fila
invoker_queue = CommandQueue()
invoker_queue.add_command(LightOnCommand(light))
invoker_queue.add_command(ConcreteCommand(receiver))
invoker_queue.add_command(LightOffCommand(light))

invoker_queue.process_commands()
# Processa comandos em sequência com delay
```

## Dicas importantes:

1. **Desacoplamento**: O padrão Command separa quem invoca (Invoker) de quem executa (Receiver)

2. **Flexibilidade**: Você pode trocar comandos em tempo de execução

3. **Composição**: Comandos podem ser compostos em macros

4. **Histórico**: Ideal para implementar undo/redo

5. **Lazy execution**: Comandos podem ser executados depois (filas, agendamentos)

## Exemplo prático completo:

```python
def main():
    # Setup
    receiver = Receiver()
    light = Light()
    invoker = Invoker()

    # Menu de comandos
    commands = {
        "1": LightOnCommand(light),
        "2": LightOffCommand(light),
        "3": ConcreteCommand(receiver),
    }

    # Simular interação do usuário
    for choice in ["1", "3", "2"]:
        print(f"\nExecutando comando {choice}")
        invoker.set_command(commands[choice])
        invoker.execute_command()

if __name__ == "__main__":
    main()
```

Este padrão é muito útil em:
- Sistemas de fila de processamento
- Botões em interfaces gráficas
- Implementação de undo/redo
- Transações em bancos de dados
- Workflows e pipelines



No `main.py`, importe as classes que ele precisa de `command.py`:

```python
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
```

Estando os dois arquivos no mesmo diretório:

```text
src/
├── main.py
└── command.py
```

execute assim:

```bash
cd src
python3 main.py
```

Saída:

```text
Luz ligada
Luz desligada
```

No seu caso, `command.py` concentra as abstrações reutilizáveis (`Command` e `Invoker`); `main.py` cria um receiver específico (`Light`) e seus comandos concretos.

Se depois você transformar `src` em pacote Python, adicione `src/__init__.py` e mude o import para:

```python
from .command import Command, Invoker
```

Nesse segundo caso, execute a partir do diretório acima de `src`:

```bash
python3 -m src.main
```
