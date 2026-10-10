
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

if __name__ == "__main__":
    unittest.main()
