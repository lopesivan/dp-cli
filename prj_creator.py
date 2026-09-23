#!/usr/bin/env python3
"""
prj_creator.py — Criador de projetos multi-linguagem, colorido e rico.

Baseado nos scripts originais:
  - prj.go     (Go, com go mod init)
  - prj.cs     (C# via dotnet CLI)
  - prj.mono   (C# compatível com Mono / .NET Framework)
  - prj.kotlin (Kotlin via gradle init)

Cada projeto criado ganha também um arquivo .yabs (config Lua de tasks
para o Neovim, no formato yabs.nvim) com atalhos coerentes com o
Makefile/toolchain de cada linguagem.

Requisitos:
    pip install rich

Uso:
    python3 prj_creator.py
"""

from __future__ import annotations

import os
import stat
import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.rule import Rule
from rich.status import Status
from rich.traceback import install as install_traceback

install_traceback(show_locals=False)
console = Console()

BANNER = r"""
[bold cyan] ____                _           _      ____                _              [/]
[bold cyan]|  _ \ _ __ ___    _(_) ___  ___| |_    / ___|_ __ ___  __ _| |_ ___  _ __  [/]
[bold cyan]| |_) | '__/ _ \  | | |/ _ \/ __| __|  | |   | '__/ _ \/ _` | __/ _ \| '__| [/]
[bold cyan]|  __/| | | (_) | | | |  __/ (__| |_   | |___| | |  __/ (_| | || (_) | |    [/]
[bold cyan]|_|   |_|  \___/  |_|_|\___|\___|\__|   \____|_|  \___|\__,_|\__\___/|_|    [/]
"""

LANGUAGES = {
    "1": ("Go", "🐹", "cyan"),
    "2": ("C# (.NET CLI)", "🟣", "magenta"),
    "3": ("C# (Mono / .NET Framework)", "🟪", "purple4"),
    "4": ("Kotlin (Gradle)", "🟠", "orange3"),
    "0": ("Sair", "🚪", "grey62"),
}


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def show_menu() -> str:
    console.print(BANNER)
    console.print(Rule(style="cyan"))

    table = Table(show_header=True,
                  header_style="bold white on dark_blue", expand=True)
    table.add_column("Opção", justify="center", style="bold yellow", width=8)
    table.add_column("Linguagem / Template", style="bold")
    table.add_column("", justify="center", width=4)

    for key, (name, emoji, color) in LANGUAGES.items():
        if key == "0":
            table.add_row(key, f"[{color}]{name}[/]", emoji)
        else:
            table.add_row(key, f"[{color}]{name}[/]", emoji)

    console.print(table)
    console.print()

    choice = Prompt.ask(
        "[bold green]Escolha a linguagem[/]",
        choices=list(LANGUAGES.keys()),
        default="1",
    )
    return choice


def ask_project_name() -> str:
    while True:
        name = Prompt.ask("[bold green]Nome do projeto[/]").strip()
        if name:
            return name
        console.print("[bold red]✗ Nome não pode ser vazio.[/]")


def dir_check(path: Path) -> bool:
    """Retorna True se pode prosseguir (diretório não existe ou usuário confirmou)."""
    if path.exists():
        console.print(
            Panel(
                f"[bold red]O diretório '{path}' já existe.[/]",
                title="⚠ Aviso",
                border_style="red",
            )
        )
        return False
    return True


def run_step(description: str, func, *args, **kwargs) -> bool:
    """Executa uma etapa mostrando spinner e resultado colorido."""
    try:
        with console.status(f"[bold cyan]{description}...", spinner="dots"):
            func(*args, **kwargs)
        console.print(f"  [bold green]✓[/] {description}")
        return True
    except subprocess.CalledProcessError as e:
        console.print(
            f"  [bold red]✗[/] {description} — falhou (código {e.returncode})")
        if e.stdout:
            console.print(f"[grey62]{e.stdout}[/]")
        if e.stderr:
            console.print(f"[red]{e.stderr}[/]")
        return False
    except Exception as e:  # noqa: BLE001
        console.print(f"  [bold red]✗[/] {description} — erro: {e}")
        return False


def write_file(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def run_cmd(cmd: list[str], cwd: Path, env: dict | None = None) -> None:
    subprocess.run(
        cmd,
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )


def yabs_task(icon_name: str, cmd: str) -> str:
    return (
        f'    ["{icon_name}"] = {{\n'
        f'      type = "lua",\n'
        f'      command = function()\n'
        f'        vim.cmd.terminal("{cmd}")\n'
        f'      end,\n'
        f'    }},\n'
    )


def build_yabs(tasks: list[tuple[str, str]]) -> str:
    body = "return {\n  tasks = {\n"
    body += "".join(yabs_task(name, cmd) for name, cmd in tasks)
    body += "  },\n}\n"
    return body


def write_yabs(path: Path, tasks: list[tuple[str, str]]) -> None:
    write_file(path / ".yabs", build_yabs(tasks))


def summary_panel(name: str, path: Path, lang: str, color: str, extra_lines: list[str]) -> None:
    body = "\n".join(
        [
            f"[bold]Projeto:[/] {name}",
            f"[bold]Linguagem:[/] {lang}",
            f"[bold]Diretório:[/] {path.resolve()}",
            "",
            *extra_lines,
        ]
    )
    console.print(Panel(body, title="🎉 Projeto criado com sucesso!",
                  border_style=color, expand=False))


# --------------------------------------------------------------------------- #
# Criadores por linguagem
# --------------------------------------------------------------------------- #

def create_go(name: str) -> None:
    path = Path(name)
    if not dir_check(path):
        return

    if not run_step("Criando diretório", path.mkdir):
        return

    main_go = '''package main

import "fmt"

func main() {
\tfmt.Println("Olá, mundo!")
}
'''

    ok = run_step("Inicializando módulo Go (go mod init mymodulo)",
                  run_cmd, ["go", "mod", "init", "mymodulo"], path)
    run_step("Gerando main.go", write_file, path / "main.go", main_go)

    run_step(
        "Gerando .yabs",
        write_yabs,
        path,
        [
            ("🔧 Init", "go mod tidy"),
            ("🛠️ Build", "go build ./..."),
            ("🚀 Run", "go run main.go"),
            ("🧪 Test", "go test ./..."),
            ("📦 Install", "go install ./..."),
            ("🧹 Clean", "go clean"),
        ],
    )

    summary_panel(
        name, path, "Go", "cyan",
        [
            "[bold]Rodar:[/] cd " + name + " && go run main.go",
            "[bold]Compilar:[/] go build",
        ],
    )


def create_cs_dotnet(name: str) -> None:
    path = Path(name)
    if not dir_check(path):
        return

    ok = run_step(
        "Criando projeto com dotnet CLI (dotnet new console)",
        run_cmd,
        ["dotnet", "new", "console", "-n", name, "--use-program-main"],
        Path("."),
    )
    if not ok:
        return

    makefile = "build:\n\tdotnet build\n\nrun:\n\tdotnet run\n\nclean:\n\tdotnet clean\n"
    csharpierrc = (
        '{\n'
        '\t"printWidth": 120,\n'
        '\t"preprocessorSymbolSets": [\n'
        '\t\t"",\n'
        '\t\t"DEBUG"\n'
        '\t],\n'
        '\t"endOfLine": "lf",\n'
        '\t"useTabs": false,\n'
        '\t"tabWidth": 4\n'
        '}\n'
    )

    run_step("Gerando Makefile", write_file, path / "Makefile", makefile)
    run_step("Gerando .csharpierrc.json", write_file,
             path / ".csharpierrc.json", csharpierrc)

    run_step(
        "Gerando .yabs",
        write_yabs,
        path,
        [
            ("🔧 Init", "dotnet restore"),
            ("🛠️ Build", "make build"),
            ("🚀 Run", "make run"),
            ("🧪 Test", "dotnet test"),
            ("📦 Publish", "dotnet publish -c Release"),
            ("🧹 Clean", "make clean"),
        ],
    )

    summary_panel(
        name, path, "C# (.NET CLI)", "magenta",
        [
            "[bold]Compilar:[/] make build   (ou dotnet build)",
            "[bold]Rodar:[/] make run        (ou dotnet run)",
        ],
    )


def create_cs_mono(name: str) -> None:
    path = Path(name)
    if not dir_check(path):
        return

    if not run_step("Criando diretório", path.mkdir):
        return

    program_cs = f'''using System;

namespace {name}
{{
    class Program
    {{
        static void Main(string[] args)
        {{
            Console.WriteLine("Olá, mundo Mono!");
        }}
    }}
}}
'''

    csproj = f'''<Project ToolsVersion="4.0" DefaultTargets="Build" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFrameworkVersion>v4.7.2</TargetFrameworkVersion>
    <AssemblyName>{name}</AssemblyName>
  </PropertyGroup>

  <ItemGroup>
    <Compile Include="Program.cs" />
  </ItemGroup>

  <Import Project="$(MSBuildToolsPath)\\Microsoft.CSharp.targets" />
</Project>
'''

    makefile = f'''CSPROJ = {name}.csproj
RELEASE = bin/Release/{name}.exe
DEBUG = bin/Debug/{name}.exe

all: debug
clean: clean-debug
run: run-debug

run-release:
\tmono $(RELEASE)

release:
\tmsbuild /p:Configuration=Release $(CSPROJ)

rebuild-release:
\tmsbuild $(CSPROJ) -t:Rebuild -p:Configuration=Release

clean-release:
\tmsbuild $(CSPROJ) -t:Clean -p:Configuration=Release

run-debug:
\tmono $(DEBUG)

debug:
\tmsbuild $(CSPROJ)

rebuild-debug:
\tmsbuild $(CSPROJ) -t:Rebuild -p:Configuration=Debug

clean-debug:
\tmsbuild $(CSPROJ) -t:Clean -p:Configuration=Debug
'''

    csharpierrc = (
        '{\n'
        '\t"printWidth": 120,\n'
        '\t"preprocessorSymbolSets": [\n'
        '\t\t"",\n'
        '\t\t"DEBUG"\n'
        '\t],\n'
        '\t"endOfLine": "lf",\n'
        '\t"useTabs": false,\n'
        '\t"tabWidth": 4\n'
        '}\n'
    )

    run_step("Gerando Program.cs", write_file, path / "Program.cs", program_cs)
    run_step(f"Gerando {name}.csproj", write_file,
             path / f"{name}.csproj", csproj)
    run_step("Gerando Makefile", write_file, path / "Makefile", makefile)
    run_step("Gerando .csharpierrc.json", write_file,
             path / ".csharpierrc.json", csharpierrc)

    run_step(
        "Gerando .yabs",
        write_yabs,
        path,
        [
            ("🛠️ Build (Debug)", "make debug"),
            ("🚀 Run (Debug)", "make run-debug"),
            ("📦 Build (Release)", "make release"),
            ("🚀 Run (Release)", "make run-release"),
            ("🔁 Rebuild (Debug)", "make rebuild-debug"),
            ("🔁 Rebuild (Release)", "make rebuild-release"),
            ("🧹 Clean (Debug)", "make clean-debug"),
            ("🗑️ Clean (Release)", "make clean-release"),
        ],
    )

    summary_panel(
        name, path, "C# (Mono)", "purple4",
        [
            "[bold]Compilar:[/] msbuild " + name + ".csproj",
            "[bold]Rodar:[/] mono bin/Debug/" + name + ".exe",
        ],
    )


def create_kotlin(name: str) -> None:
    path = Path(name)
    if not dir_check(path):
        return

    if not run_step("Criando diretório", path.mkdir):
        return

    gradle_home_candidates = [
        "/opt/gradle/gradle-9.4.1/bin",
        "/opt/gradle/gradle-8.13/bin",
        "/opt/gradle/gradle-8.10.2/bin",
    ]
    gradle_home = next((g for g in gradle_home_candidates if Path(
        g).exists()), gradle_home_candidates[0])

    vars_content = (
        "#GRADLE_HOME=/opt/gradle/gradle-8.10.2/bin\n"
        "#GRADLE_HOME=/opt/gradle/gradle-8.13/bin\n"
        f"GRADLE_HOME={gradle_home}\n"
        "PATH={PATH}:{GRADLE_HOME}\n"
    )
    run_step("Gerando .vars", write_file, path / ".vars", vars_content)

    env = os.environ.copy()
    env["PATH"] = f"{gradle_home}:{env.get('PATH', '')}"

    run_step(
        "Gerando .yabs",
        write_yabs,
        path,
        [
            ("🔧 Init", "make init"),
            ("🛠️ Build", "make build"),
            ("🚀 Run", "make run"),
            ("🧪 Test", "./gradlew test"),
            ("📦 Install", "./gradlew installDist"),
            ("🧹 Clean", "./gradlew clean"),
        ],
    )

    summary_panel(
        name, path, "Kotlin (Gradle)", "orange3",
        [
            "[bold]Rodar:[/] cd " + name + " && ./gradlew run",
            "[bold]Nota:[/] ajuste GRADLE_HOME em .vars se necessário",
        ],
    )

    # ------------------------------------------------------------------
    # bootstrap
    # ------------------------------------------------------------------
    bootstrap_path = path / "bootstrap"

    bootstrap_path.parent.mkdir(parents=True, exist_ok=True)

    bootstrap_script = '''#!/usr/bin/env bash
set -e # Encerra em caso de erro
set -u # Trata variáveis não definidas como erro
set -o pipefail

gradle init --type kotlin-application

exit 0
'''

    bootstrap_path.write_text(bootstrap_script)
    bootstrap_path.chmod(bootstrap_path.stat().st_mode | stat.S_IEXEC)

    # ------------------------------------------------------------------
    # Makefile
    # ------------------------------------------------------------------
    makefile_content = '''SHELL := /usr/bin/env bash

##############################################################################
# GRADLE WRAPPER
##############################################################################
GRADLE_VERSION := 9.7.1

GRADLEW       := ./gradlew
WRAPPER_JAR   := gradle/wrapper/gradle-wrapper.jar
WRAPPER_PROPS := gradle/wrapper/gradle-wrapper.properties

GRADLE_BASE_URL := https://raw.githubusercontent.com/gradle/gradle/v$(GRADLE_VERSION)

export JAVA_HOME ?= /home/ivan/.jenv/versions/21

.DEFAULT_GOAL := help

.PHONY: help init configure build run test clean tasks env

##############################################################################
# HELP
##############################################################################

help: ## mostra esta ajuda
\t@echo "Uso:"
\t@grep -hE '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) \\
\t\t| sort \\
\t\t| awk 'BEGIN {FS = ":.*?## "}; {printf "  \\033[36m%-12s\\033[0m %s\\n", $$1, $$2}'

##############################################################################
# GRADLE
##############################################################################

configure: init ## configura o projeto e cria/atualiza o .gitignore
\t@touch .gitignore
\t@for entry in \\
\t\t'build/' \\
\t\t'gradle/wrapper/' \\
\t\t'**/build/' \\
\t\t'.gradle/' \\
\t\t'.idea/' \\
\t\t'*.iml'; do \\
\t\tgrep -qxF "$$entry" .gitignore || echo "$$entry" >> .gitignore; \\
\tdone
\t@echo "==> Projeto configurado"


init: ## prepara o Gradle Wrapper
\t@command -v java >/dev/null || { echo "Erro: Java nao encontrado"; exit 1; }
\t@command -v curl >/dev/null || { echo "Erro: curl nao encontrado"; exit 1; }

\t@mkdir -p gradle/wrapper

\t@if [[ ! -f "$(WRAPPER_JAR)" ]]; then \\
\t\techo "==> Baixando gradle-wrapper.jar"; \\
\t\tcurl -fL \\
\t\t\t"$(GRADLE_BASE_URL)/gradle/wrapper/gradle-wrapper.jar" \\
\t\t\t-o "$(WRAPPER_JAR)"; \\
\tfi

\t@if [[ ! -f "$(GRADLEW)" ]]; then \\
\t\techo "==> Baixando gradlew"; \\
\t\tcurl -fL \\
\t\t\t"$(GRADLE_BASE_URL)/gradlew" \\
\t\t\t-o "$(GRADLEW)"; \\
\tfi

\t@if [[ ! -f "$(WRAPPER_PROPS)" ]] || \\
\t    ! grep -q "gradle-$(GRADLE_VERSION)-bin.zip" "$(WRAPPER_PROPS)"; then \\
\t\techo "==> Criando $(WRAPPER_PROPS)"; \\
\t\tprintf '%s\\n' \\
\t\t\t'distributionBase=GRADLE_USER_HOME' \\
\t\t\t'distributionPath=wrapper/dists' \\
\t\t\t'distributionUrl=https\\://services.gradle.org/distributions/gradle-$(GRADLE_VERSION)-bin.zip' \\
\t\t\t'networkTimeout=10000' \\
\t\t\t'validateDistributionUrl=true' \\
\t\t\t'zipStoreBase=GRADLE_USER_HOME' \\
\t\t\t'zipStorePath=wrapper/dists' \\
\t\t\t> "$(WRAPPER_PROPS)"; \\
\tfi

\t@chmod +x "$(GRADLEW)"
\t@$(GRADLEW) --version

##############################################################################
# BUILD
##############################################################################

build: ## compila o projeto
\t@$(GRADLEW) build

run: ## executa a aplicacao
\t@$(GRADLEW) run

test: ## executa os testes
\t@$(GRADLEW) test

clean: ## remove os artefatos de compilacao
\t@$(GRADLEW) clean

tasks: ## mostra as tarefas Gradle
\t@$(GRADLEW) tasks

env: ## mostra o ambiente Java/Gradle
\t@echo "JAVA_HOME = $${JAVA_HOME:-<vazio>}"
\t@echo
\t@java -version
\t@echo
\t@$(GRADLEW) --version
'''

    run_step("Gerando Makefile", write_file,
             path / "Makefile", makefile_content)


CREATORS = {
    "1": create_go,
    "2": create_cs_dotnet,
    "3": create_cs_mono,
    "4": create_kotlin,
}


# --------------------------------------------------------------------------- #
# Main loop
# --------------------------------------------------------------------------- #

def main() -> None:
    while True:
        choice = show_menu()

        if choice == "0":
            console.print("\n[bold cyan]Até logo! 👋[/]\n")
            break

        name, lang_label, color = LANGUAGES[choice]
        console.print(Rule(f"[bold {color}]{lang_label}[/]", style=color))

        project_name = ask_project_name()
        CREATORS[choice](project_name)

        console.print()
        if not Confirm.ask("[bold]Criar outro projeto?[/]", default=True):
            console.print("\n[bold cyan]Até logo! 👋[/]\n")
            break
        console.clear()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Cancelado pelo usuário.[/]")
        sys.exit(130)
