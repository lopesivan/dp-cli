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
