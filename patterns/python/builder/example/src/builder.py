from abc import ABC, abstractmethod


class Product:
    def __init__(self) -> None:
        self.part_a: str | None = None
        self.part_b: str | None = None


class Builder(ABC):
    @abstractmethod
    def build_part_a(self) -> None:
        ...

    @abstractmethod
    def build_part_b(self) -> None:
        ...

    @abstractmethod
    def get_result(self) -> Product:
        ...


class ConcreteBuilder(Builder):
    def __init__(self) -> None:
        self._product = Product()

    def build_part_a(self) -> None:
        self._product.part_a = "partA"

    def build_part_b(self) -> None:
        self._product.part_b = "partB"

    def get_result(self) -> Product:
        return self._product


class Director:
    def __init__(self, builder: Builder) -> None:
        self._builder = builder

    def construct(self) -> None:
        self._builder.build_part_a()
        self._builder.build_part_b()
