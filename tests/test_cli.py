import tempfile
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from devtool.cli import doctor_exit_code
from devtool import cli
import socket
from contextlib import redirect_stdout
from io import StringIO
from devtool import cli

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

    @patch("devtool.cli.check_python", return_value=False)
    @patch("devtool.cli.check_git", return_value=True)
    @patch("devtool.cli.check_disk_space", return_value=True)
    @patch("sys.argv", ["devtool", "doctor"])
    def test_doctor_returns_failure_when_required_check_fails(
        self, mock_disk, mock_git, mock_python
    ):
        result = cli.main()
        self.assertEqual(result, 1)

    def test_doctor_exit_code_all_checks_pass(self):
        self.assertEqual(doctor_exit_code([True, True, True]), 0)

    def test_doctor_exit_code_required_check_fails(self):
        self.assertEqual(doctor_exit_code([True, False, True]), 1)

    def test_doctor_exit_code_multiple_checks_fail(self):
        self.assertEqual(doctor_exit_code([False, False, True]), 1)

    @patch(
    "devtool.cli.socket.getaddrinfo",
    return_value=[
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("192.0.2.10", 0)),
        (socket.AF_INET, socket.SOCK_DGRAM, 17, "", ("192.0.2.10", 0)),
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("192.0.2.20", 0)),
    ],
    )
    def test_network_command_deduplicates_addresses(self, mock_dns):
        output = StringIO()

        with redirect_stdout(output):
            result = cli.resolve_hostname("example.test")

        self.assertEqual(result, 0)
        self.assertIn("192.0.2.10", output.getvalue())
        self.assertIn("192.0.2.20", output.getvalue())
        self.assertEqual(output.getvalue().count("192.0.2.10"), 1)
        mock_dns.assert_called_once_with("example.test", None)


    @patch(
       "devtool.cli.socket.getaddrinfo",
       side_effect=socket.gaierror("Name resolution failed"),
    )
    def test_network_command_handles_dns_failure(self, mock_dns):
       result = cli.resolve_hostname("invalid.example")

       self.assertEqual(result, 1)
       mock_dns.assert_called_once_with("invalid.example", None)


    @patch("devtool.cli.socket.create_connection")
    def test_tcp_connection_success(self, mock_connect):
        result = cli.check_tcp_connection("example.com", 443)

        self.assertEqual(result, 0)
        mock_connect.assert_called_once_with(
            ("example.com", 443),
            timeout=3,
        )

    @patch(
        "devtool.cli.socket.create_connection",
        side_effect=OSError("Connection refused"),
    )
    def test_tcp_connection_failure(self, mock_connect):
        output = StringIO()

        with redirect_stdout(output):
            result = cli.check_tcp_connection("example.com", 443)

        self.assertEqual(result, 1)
        self.assertIn("failed", output.getvalue())


    def test_parse_single_port(self):
        self.assertEqual(cli.parse_port_range("22"), [22])

    def test_parse_port_range(self):
        self.assertEqual(
            cli.parse_port_range("20-23"),
            [20, 21, 22, 23],
        )

    def test_parse_port_range_with_whitespace(self):
        self.assertEqual(
            cli.parse_port_range(" 20-23 "),
            [20, 21, 22, 23],
        )

    def test_parse_invalid_port_text(self):
        with self.assertRaises(ValueError):
            cli.parse_port_range("hello")

    def test_parse_port_zero(self):
        with self.assertRaises(ValueError):
            cli.parse_port_range("0")

    def test_parse_port_above_maximum(self):
        with self.assertRaises(ValueError):
            cli.parse_port_range("65536")

    def test_parse_reversed_port_range(self):
        with self.assertRaises(ValueError):
            cli.parse_port_range("80-20")

    def test_parse_malformed_port_range(self):
        with self.assertRaises(ValueError):
            cli.parse_port_range("20-23-25")

    @patch("devtool.cli.socket.create_connection")
    def test_tcp_port_open(self, mock_connect):
        self.assertTrue(cli.is_tcp_port_open("127.0.0.1", 22))
        mock_connect.assert_called_once_with(
            ("127.0.0.1", 22),
            timeout=0.5,
        )

    @patch(
        "devtool.cli.socket.create_connection",
        side_effect=OSError("Connection refused"),
    )
    def test_tcp_port_not_open(self, mock_connect):
        self.assertFalse(cli.is_tcp_port_open("127.0.0.1", 22))


    @patch("devtool.cli.is_tcp_port_open")
    def test_scan_ports_reports_open_ports(self, mock_is_open):
        mock_is_open.side_effect = [False, True, False]

        output = StringIO()
        with redirect_stdout(output):
            result = cli.scan_ports("127.0.0.1", "20-22")

        self.assertEqual(result, 0)
        self.assertIn("Port 21: OPEN", output.getvalue())
        self.assertNotIn("Port 20: OPEN", output.getvalue())
        self.assertNotIn("Port 22: OPEN", output.getvalue())
        self.assertIn("Found 1 open port(s)", output.getvalue())

    @patch("devtool.cli.is_tcp_port_open")
    def test_scan_ports_rejects_invalid_range(self, mock_is_open):
        output = StringIO()
        with redirect_stdout(output):
            result = cli.scan_ports("127.0.0.1", "hello")

        self.assertEqual(result, 1)
        self.assertIn("Invalid port range", output.getvalue())
        mock_is_open.assert_not_called()


    @patch("devtool.cli.scan_ports", return_value=0)
    @patch("sys.argv", ["devtool", "scan", "127.0.0.1", "--ports", "22"])
    def test_scan_command_dispatches(self, mock_scan):
        result = cli.main()

        self.assertEqual(result, 0)
        mock_scan.assert_called_once_with("127.0.0.1", "22")



if __name__ == "__main__":
    unittest.main()
