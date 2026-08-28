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


class Director:
    def __init__(self, builder: Builder) -> None:
        self._builder = builder

    def construct(self) -> None:
        self._builder.build_part_a()
        self._builder.build_part_b()


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
