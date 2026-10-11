from pathlib import Path
import argparse
import platform
import sys
import shutil
import subprocess


def show_system_info():
    """Display basic information about this computer."""
    print(f"Operating system: {platform.system()}")
    print(f"OS release: {platform.release()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Python version: {platform.python_version()}")


def main():
    parser = argparse.ArgumentParser(
        prog="devtool",
        description="A lightweight toolkit for developers",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="devtool 0.1.0",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
    )

    subparsers.add_parser(
        "system",
        help="Display system information",
    )
    subparsers.add_parser(
    "doctor",
    help="Check the development environment",
    )
    files_parser = subparsers.add_parser(
    "files",
    help="List files recursively in a directory",
    )

    files_parser.add_argument(
    "directory",
    nargs="?",
    default=".",
    help="Directory to search (default: current directory)",
    )

    args = parser.parse_args()

    if args.command == "system":
        show_system_info()
    elif args.command == "doctor":
        check_python()
        check_git()
        check_disk_space()
    elif args.command is None:
        parser.print_help()
    elif args.command == "files":
        find_files(args.directory)


def check_python():
    """Check whether the Python version meets the project requirement."""
    version = sys.version_info

    print(f"Python version: {platform.python_version()}")

    if version >= (3, 10):
        print("PASS: Python 3.10 or newer is installed.")
    else:
        print("WARN: Python 3.10 or newer is required.")


def check_git():
    """Check whether Git is installed and available."""
    git_path = shutil.which("git")

    if git_path is None:
        print("WARN: Git was not found on PATH.")
        return

    result = subprocess.run(
        ["git", "--version"],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode == 0:
        print(f"PASS: {result.stdout.strip()}")
    else:
        print("WARN: Git was found, but its version check failed.")


def check_disk_space():
    """Report available disk space for the current directory."""
    usage = shutil.disk_usage(Path.cwd())
    free_gib = usage.free / (1024 ** 3)

    print(f"Free disk space: {free_gib:.1f} GiB")

    if free_gib >= 2:
        print("PASS: At least 2 GiB of disk space is available.")
    else:
        print("WARN: Less than 2 GiB of disk space is available.")



def find_files(directory):
    """Find project files while skipping generated directories."""
    root = Path(directory)

    if not root.exists():
        print(f"Error: '{directory}' does not exist.")
        return

    if not root.is_dir():
        print(f"Error: '{directory}' is not a directory.")
        return

    ignored_dirs = {
        ".git",
        ".venv",
        "__pycache__",
        "*.egg-info",
    }

    for current_dir, dir_names, file_names in root.walk():
        dir_names[:] = [
            name
            for name in dir_names
            if name not in ignored_dirs
            and not name.endswith(".egg-info")
        ]

        for file_name in file_names:
            print(current_dir / file_name)


if __name__ == "__main__":
    main()