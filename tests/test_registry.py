"""Registry discovery tests."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from core.registry import discover_patterns


PROJECT_DIR = Path(__file__).resolve().parents[1]


class RegistryTests(unittest.TestCase):
    """Verify filesystem-based pattern discovery."""

    def test_discovers_all_built_in_patterns(self) -> None:
        registry = discover_patterns(PROJECT_DIR / "patterns")

        self.assertEqual(set(registry), {"java", "cpp", "python"})
        self.assertEqual(
            set(registry["java"]),
            {"singleton", "factory", "observer"},
        )
        self.assertEqual(set(registry["cpp"]), {"singleton"})
        self.assertEqual(set(registry["python"]), {"singleton"})

    def test_ignores_incomplete_pattern_directories(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "java" / "broken" / "templates").mkdir(parents=True)

            registry = discover_patterns(root)

        self.assertEqual(registry, {})


if __name__ == "__main__":
    unittest.main()
