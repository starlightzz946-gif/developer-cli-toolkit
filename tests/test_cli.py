import tempfile
import subprocess
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLI_FILE = PROJECT_ROOT / "src" / "devtool" / "cli.py"


def run_cli(*args):
    return subprocess.run(
        [sys.executable, str(CLI_FILE), *args],
        capture_output=True,
        text=True,
        check=False,
    )


class TestDevtoolCLI(unittest.TestCase):

    def test_version(self):
        result = run_cli("--version")
        self.assertEqual(result.returncode, 0)
        self.assertIn("devtool 0.1.0", result.stdout)

    def test_system_command(self):
        result = run_cli("system")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Operating system:", result.stdout)
        self.assertIn("Architecture:", result.stdout)

    def test_help(self):
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("system", result.stdout)
 
    def test_doctor_command(self):
        result = run_cli("doctor")

        self.assertEqual(result.returncode, 0)
        self.assertIn("Python version:", result.stdout)
        self.assertIn("git version", result.stdout)
        self.assertIn("Free disk space:", result.stdout)

    
    def test_files_command(self):
        result = run_cli("files", str(PROJECT_ROOT))

        self.assertEqual(result.returncode, 0)
        self.assertIn("README.md", result.stdout)
        self.assertIn("pyproject.toml", result.stdout)

    def test_files_ignores_generated_directories(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            (root / "README.md").write_text("Project readme")
            (root / ".venv").mkdir()
            (root / ".venv" / "generated.txt").write_text("Generated")
            (root / ".git").mkdir()
            (root / ".git" / "internal.txt").write_text("Git data")
            (root / "package.egg-info").mkdir()
            (root / "package.egg-info" / "metadata.txt").write_text("Metadata")

            result = run_cli("files", str(root))

            self.assertIn("README.md", result.stdout)
            self.assertNotIn("generated.txt", result.stdout)
            self.assertNotIn("internal.txt", result.stdout)
            self.assertNotIn("metadata.txt", result.stdout)

    def test_files_nonexistent_directory(self):
        result = run_cli("files", "/path/that/does/not/exist")

        self.assertIn("does not exist", result.stdout)

    def test_files_path_is_not_directory(self):
        with tempfile.NamedTemporaryFile() as temp_file:
            result = run_cli("files", temp_file.name)

            self.assertIn("is not a directory", result.stdout)


if __name__ == "__main__":
    unittest.main()
