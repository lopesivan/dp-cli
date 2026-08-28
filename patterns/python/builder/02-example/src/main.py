from builder import Director, HtmlReportBuilder, TextReportBuilder


def main() -> None:
    text_builder = TextReportBuilder()
    director = Director(text_builder)
    director.construct()
    text_report = text_builder.get_result()
    print(text_report.part_a)  # Cabeçalho em texto
    print(text_report.part_b)  # Rodapé em texto

    html_builder = HtmlReportBuilder()
    director = Director(html_builder)
    director.construct()
    html_report = html_builder.get_result()
    print(html_report.part_a)  # <header>Relatório</header>
    print(html_report.part_b)  # <footer>Fim</footer>


if __name__ == "__main__":
    main()
