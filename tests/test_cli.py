import tempfile
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

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

    
    def test_git_command_clean_repository(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            subprocess.run(
                ["git", "init", "-q", str(root)],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(root), "config", "user.name", "Test"],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(root), "config", "user.email", "test@example.com"],
                check=True,
            )

            (root / "README.md").write_text("Test project\n")
            subprocess.run(
                ["git", "-C", str(root), "add", "README.md"],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(root), "commit", "-qm", "Initial commit"],
                check=True,
            )

            result = subprocess.run(
                [sys.executable, str(CLI_FILE), "git"],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0)
            self.assertIn("Branch:", result.stdout)
            self.assertIn("Working tree: clean", result.stdout)

    def test_git_command_detects_changes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            subprocess.run(
                ["git", "init", "-q", str(root)],
                check=True,
            )
            (root / "new_file.txt").write_text("Untracked file\n")

            result = subprocess.run(
                [sys.executable, str(CLI_FILE), "git"],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0)
            self.assertIn("Working tree: changes detected", result.stdout)

    def test_git_command_outside_repository(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [sys.executable, str(CLI_FILE), "git"],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertIn("Error:", result.stdout)
            self.assertIn("not a git repository", result.stdout.lower())
    
    @patch("devtool.cli.shutil.which", return_value=None)
    def test_git_command_git_not_available(self, mock_which):
        from devtool.cli import show_git_status
        from io import StringIO
        from contextlib import redirect_stdout

        output = StringIO()

        with redirect_stdout(output):
            show_git_status()

        self.assertIn(
            "Git is not installed or not available on PATH",
            output.getvalue(),
        )
        mock_which.assert_called_once_with("git")



if __name__ == "__main__":
    unittest.main()
