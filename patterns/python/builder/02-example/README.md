Aqui está um exemplo completo de como usar essa classe Builder:

```python
# Exemplo de uso do padrão Builder

# 1. Criar o ConcreteBuilder
builder = ConcreteBuilder()

# 2. Criar o Director e passar o builder
director = Director(builder)

# 3. Mandar o Director construir o produto
director.construct()

# 4. Recuperar o resultado final
product = builder.get_result()

print(product.part_a)  # Saída: partA
print(product.part_b)  # Saída: partB
```

## Exemplos mais elaborados:

### Exemplo 1: Builder com múltiplas partes e fluent interface

```python
class Pizza:
    def __init__(self) -> None:
        self.size: str | None = None
        self.toppings: list[str] = []

    def __str__(self) -> str:
        return f"Pizza {self.size} com {', '.join(self.toppings)}"


class PizzaBuilder(Builder):
    def __init__(self) -> None:
        self._pizza = Pizza()

    def set_size(self, size: str) -> "PizzaBuilder":
        self._pizza.size = size
        return self

    def add_topping(self, topping: str) -> "PizzaBuilder":
        self._pizza.toppings.append(topping)
        return self

    def build_part_a(self) -> None:
        self._pizza.size = "média"

    def build_part_b(self) -> None:
        self._pizza.toppings.append("queijo")

    def get_result(self) -> Pizza:
        return self._pizza

# Uso com fluent interface (sem Director)
pizza = (
    PizzaBuilder()
    .set_size("grande")
    .add_topping("calabresa")
    .add_topping("cebola")
    .get_result()
)
print(pizza)  # Saída: Pizza grande com calabresa, cebola
```

### Exemplo 2: Múltiplos ConcreteBuilders com o mesmo Director

```python
class TextReportBuilder(Builder):
    def __init__(self) -> None:
        self._product = Product()

    def build_part_a(self) -> None:
        self._product.part_a = "Cabeçalho em texto"

    def build_part_b(self) -> None:
        self._product.part_b = "Rodapé em texto"

    def get_result(self) -> Product:
        return self._product


class HtmlReportBuilder(Builder):
    def __init__(self) -> None:
        self._product = Product()

    def build_part_a(self) -> None:
        self._product.part_a = "<header>Relatório</header>"

    def build_part_b(self) -> None:
        self._product.part_b = "<footer>Fim</footer>"

    def get_result(self) -> Product:
        return self._product

# Uso: o mesmo Director gera saídas diferentes trocando o builder
director = Director(TextReportBuilder())
director.construct()
print(director._builder.get_result().part_a)  # Cabeçalho em texto

director = Director(HtmlReportBuilder())
director.construct()
print(director._builder.get_result().part_a)  # <header>Relatório</header>
```

### Exemplo 3: Validação antes de liberar o resultado

```python
class ValidatingBuilder(Builder):
    def __init__(self) -> None:
        self._product = Product()

    def build_part_a(self) -> None:
        self._product.part_a = "partA"

    def build_part_b(self) -> None:
        self._product.part_b = "partB"

    def get_result(self) -> Product:
        if self._product.part_a is None or self._product.part_b is None:
            raise ValueError("Produto incompleto: rode construct() antes de get_result()")
        return self._product

# Uso
builder = ValidatingBuilder()
try:
    builder.get_result()  # ainda não construído
except ValueError as error:
    print(error)  # Saída: Produto incompleto: rode construct() antes de get_result()

director = Director(builder)
director.construct()
print(builder.get_result())  # agora funciona
```

## Dicas importantes:

1. **Separação de responsabilidades**: o `Director` sabe
a *ordem* de construção; o `Builder` sabe *como* construir
cada parte

2. **Reuso**: o mesmo `Director` funciona com qualquer
`ConcreteBuilder` que implemente a interface `Builder`

3. **Builder sem Director**: nada impede usar o `Builder`
isolado (fluent interface), pulando o `Director` quando a
ordem de construção é sempre a mesma

4. **Imutabilidade**: `get_result()` pode devolver uma cópia
ou objeto congelado, evitando que o builder seja reaproveitado
por engano

5. **Validação**: `get_result()` é um bom lugar pra garantir
que o produto está completo antes de liberá-lo

Este padrão é muito útil em:
- Construção de objetos complexos com muitos parâmetros opcionais
- Geração de relatórios/documentos em formatos diferentes a partir do mesmo processo
- Parsers e montadores de configuração (ex: query builders, request builders)
- Testes: builders de objetos de teste com valores padrão sobrescrevíveis

## Exemplo prático completo:

No `main.py`, importe as classes que ele precisa de `builder.py`:

```python
from builder import ConcreteBuilder, Director


def main() -> None:
    builder = ConcreteBuilder()
    director = Director(builder)

    director.construct()
    product = builder.get_result()

    print(product.part_a)
    print(product.part_b)


if __name__ == "__main__":
    main()
```

Estando os dois arquivos no mesmo diretório:

```text
src/
├── main.py
└── builder.py
```

execute assim:

```bash
cd src
python3 main.py
```

Saída:

```text
partA
partB
```

No seu caso, `builder.py` concentra as abstrações reutilizáveis (`Product`, `Builder`, `Director`); `main.py` escolhe o `ConcreteBuilder` e dispara a construção.

Se depois você transformar `src` em pacote Python, adicione `src/__init__.py` e mude o import para:

```python
from .builder import ConcreteBuilder, Director
```

Nesse segundo caso, execute a partir do diretório acima de `src`:

```bash
python3 -m src.main
```
