"""End-to-end CLI tests."""

from __future__ import annotations

from contextlib import contextmanager, redirect_stdout
from io import StringIO
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterator, Sequence
import unittest

import yaml

import dp


@contextmanager
def working_directory(path: Path) -> Iterator[None]:
    """Temporarily change the process working directory."""
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def run_cli(arguments: Sequence[str], directory: Path) -> tuple[int, str]:
    """Run the CLI in a temporary working directory."""
    output = StringIO()
    with working_directory(directory), redirect_stdout(output):
        result = dp.main(arguments)
    return result, output.getvalue()


def read_yaml(path: Path) -> dict[str, object]:
    """Read a YAML mapping used by a test."""
    content = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(content, dict):
        raise AssertionError("expected a YAML mapping")
    return content


def write_yaml(path: Path, content: dict[str, object]) -> None:
    """Write a YAML mapping used by a test."""
    path.write_text(
        yaml.safe_dump(content, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


class CliTests(unittest.TestCase):
    """Verify the two-stage generation flow."""

    def test_java_singleton_flow(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)

            status, first_output = run_cli(["--java", "singleton"], root)

            self.assertEqual(status, 0)
            self.assertIn("Criado: key.yaml", first_output)
            self.assertTrue((root / "key.yaml").is_file())
            self.assertFalse((root / "src").exists())

            config = read_yaml(root / "key.yaml")
            config.update(
                {
                    "package": "br.eng.ivanlopes.patterns",
                    "class_name": "AppSingleton",
                    "output_dir": "src/main/java/br/eng/ivanlopes/patterns",
                }
            )
            write_yaml(root / "key.yaml", config)

            status, second_output = run_cli(["--java", "singleton"], root)
            generated = (
                root
                / "src/main/java/br/eng/ivanlopes/patterns/AppSingleton.java"
            )

            self.assertEqual(status, 0)
            self.assertIn("Gerado:", second_output)
            self.assertTrue(generated.is_file())
            source = generated.read_text(encoding="utf-8")
            self.assertIn("package br.eng.ivanlopes.patterns;", source)
            self.assertIn("public final class AppSingleton", source)
            self.assertIn("synchronized (AppSingleton.class)", source)

    def test_missing_required_field_uses_and_persists_default(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            run_cli(["--java", "singleton"], root)
            config = read_yaml(root / "key.yaml")
            del config["class_name"]
            write_yaml(root / "key.yaml", config)

            status, output = run_cli(["--java", "singleton"], root)

            self.assertEqual(status, 0)
            self.assertIn("Campo ausente: class_name", output)
            self.assertEqual(read_yaml(root / "key.yaml")["class_name"], "Singleton")
            self.assertTrue(
                (root / "src/main/java/com/example/app/Singleton.java").is_file()
            )

    def test_generation_is_idempotent(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            run_cli(["--python", "singleton"], root)
            run_cli(["--python", "singleton"], root)
            generated = root / "singleton.py"
            generated.write_text("conteúdo antigo\n", encoding="utf-8")

            status, _ = run_cli(["--python", "singleton", "--force"], root)

            self.assertEqual(status, 0)
            self.assertIn(
                "class Singleton:",
                generated.read_text(encoding="utf-8"),
            )

    def test_all_initial_patterns_render(self) -> None:
        selections = [
            ("java", "factory"),
            ("java", "observer"),
            ("cpp", "singleton"),
        ]
        for language, pattern in selections:
            with self.subTest(language=language, pattern=pattern):
                with TemporaryDirectory() as temporary:
                    root = Path(temporary)
                    arguments = [f"--{language}", pattern]

                    run_cli(arguments, root)
                    status, output = run_cli(arguments, root)

                    self.assertEqual(status, 0)
                    self.assertIn("Gerado:", output)


if __name__ == "__main__":
    unittest.main()
