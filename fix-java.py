from pathlib import Path
import re

prefixo_antigo = "{{ output_dir }}/"
prefixo_novo = "{{ output_dir }}/{{ package | replace('.', '/') }}/"

for arquivo in sorted(Path("patterns/java").glob("*/meta.yaml")):
    original = arquivo.read_text(encoding="utf-8")

    atualizado = re.sub(
        r"(?m)^([ \t]*default: )src/main/java/com/example/app[ \t]*$",
        r"\1src/main/java",
        original,
    )

    def corrigir_saida(match):
        indentacao = match.group("indentacao")
        caminho = match.group("caminho")

        if caminho.startswith(prefixo_novo):
            return match.group(0)

        if caminho.startswith(prefixo_antigo):
            caminho = prefixo_novo + caminho[len(prefixo_antigo):]
            return f'{indentacao}output_path: "{caminho}"'

        return match.group(0)

    atualizado = re.sub(
        r"""(?m)^(?P<indentacao>[ \t]*)output_path: """
        r"""(?P<aspas>["'])(?P<caminho>.*)(?P=aspas)[ \t]*$""",
        corrigir_saida,
        atualizado,
    )

    if atualizado != original:
        arquivo.write_text(atualizado, encoding="utf-8")
        print(f"Atualizado: {arquivo}")
    else:
        print(f"Sem alteração: {arquivo}")
