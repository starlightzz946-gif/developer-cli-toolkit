from pathlib import Path
import argparse
import platform
import sys
import shutil
import subprocess
import os
import socket


def show_system_info():
    """Display basic information about this computer."""
    print(f"Operating system: {platform.system()}")
    print(f"OS release: {platform.release()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Python version: {platform.python_version()}")


def doctor_exit_code(checks_passed):
    """Return success only when all required checks pass."""
    return 0 if all(checks_passed) else 1


def resolve_hostname(hostname):
    """Resolve a hostname and display its unique IP addresses."""
    try:
        results = socket.getaddrinfo(hostname, None)
    except socket.gaierror as error:
        print(f"DNS lookup failed for {hostname}: {error}")
        return 1

    addresses = sorted({
        result[4][0]
        for result in results
    })

    if not addresses:
        print(f"No IP addresses found for {hostname}.")
        return 1

    print(f"Hostname: {hostname}")
    print("IP addresses:")

    for address in addresses:
        print(f"- {address}")

    return 0


def check_tcp_connection(hostname, port, timeout=3):
    """Check whether a TCP connection can be established."""
    try:
        with socket.create_connection(
            (hostname, port),
            timeout=timeout,
        ):
            print(f"TCP connection to {hostname}:{port} succeeded.")
            return 0
    except (socket.gaierror, OSError, TimeoutError) as error:
        print(f"TCP connection to {hostname}:{port} failed: {error}")
        return 1


def parse_port_range(port_spec):
    """Parse and validate a single TCP port or a port range."""
    port_spec = port_spec.strip()

    if not port_spec:
        raise ValueError("Port specification cannot be empty.")

    if "-" in port_spec:
        parts = port_spec.split("-")

        if len(parts) != 2:
            raise ValueError("Use a port like 22 or a range like 20-23.")

        start_text, end_text = parts
    else:
        start_text = end_text = port_spec

    try:
        start_port = int(start_text)
        end_port = int(end_text)
    except ValueError:
        raise ValueError(
            "Ports must be integers, like 22 or 20-23."
        ) from None

    if not (1 <= start_port <= 65535):
        raise ValueError("Ports must be between 1 and 65535.")

    if not (1 <= end_port <= 65535):
        raise ValueError("Ports must be between 1 and 65535.")

    if start_port > end_port:
        raise ValueError("The starting port cannot exceed the ending port.")

    return list(range(start_port, end_port + 1))


def is_tcp_port_open(hostname, port, timeout=0.5):
    """Return True if a TCP connection to the port succeeds."""
    try:
        with socket.create_connection(
            (hostname, port),
            timeout=timeout,
        ):
            return True
    except OSError:
        return False

def get_service_name(port):
    """Return the common service name for a TCP port."""

    services = {
        22: "SSH",
        53: "DNS",
        80: "HTTP",
        443: "HTTPS",
        3306: "MySQL",
    }

    return services.get(port, "Unknown")


def scan_ports(hostname, port_spec):
    """Scan a specified TCP port or range on a host."""
    try:
        ports = parse_port_range(port_spec)
    except ValueError as error:
        print(f"Invalid port range: {error}")
        return 1

    print(f"Scanning {hostname}...")

    open_ports = []

    for port in ports:
        if is_tcp_port_open(hostname, port):
            print(f"Port {port}: OPEN ({get_service_name(port)})")
            open_ports.append(port)

    print(f"Scan complete. Found {len(open_ports)} open port(s).")
    return 0


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

    subparsers.add_parser(
    "git",
    help="Display Git branch and working-tree status",
    )

    scan_parser = subparsers.add_parser(
        "scan",
        help="Scan TCP ports on an authorized host",
    )

    scan_parser.add_argument(
        "hostname",
        help="Hostname or IP address to scan",
    )

    scan_parser.add_argument(
        "--ports",
        default="1-1024",
        help="Port or port range to scan (default: 1-1024)",
    )



    network_parser = subparsers.add_parser(
        "network",
        help="Resolve a hostname to IP addresses or check connectivity",
    )

    network_parser.add_argument(
        "hostname",
        help="Hostname to resolve or check",
    )

    network_parser.add_argument(
        "--check",
        action="store_true",
        help="Check TCP connectivity to the hostname",
    )

    network_parser.add_argument(
        "--port",
        type=int,
        default=443,
        help="TCP port to check (default: 443)",
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
        checks_passed = [
            check_python(),
            check_git(),
            check_disk_space(),
        ]

        return doctor_exit_code(checks_passed)
    elif args.command is None:
        parser.print_help()
    elif args.command == "files":
        find_files(args.directory)
    elif args.command == "git":
        show_git_status()
    elif args.command == "network":
        if args.check:
            return check_tcp_connection(args.hostname, args.port)

        return resolve_hostname(args.hostname)
    elif args.command == "scan":
        return scan_ports(args.hostname, args.ports)



def check_python():
    """Check whether the Python version meets the project requirement."""
    version = sys.version_info

    print(f"Python version: {platform.python_version()}")

    if version >= (3, 10):
        print("PASS: Python 3.10 or newer is installed.")
        return True

    print("FAIL: Python 3.10 or newer is required.")
    return False




def check_git():
    """Check whether Git is installed and available."""
    if shutil.which("git") is None:
        print("FAIL: Git was not found on PATH.")
        return False

    result = subprocess.run(
        ["git", "--version"],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode == 0:
        print(f"PASS: {result.stdout.strip()}")
        return True

    print("FAIL: Git was found, but its version check failed.")
    return False




def check_disk_space():
    """Report available disk space for the current directory."""
    usage = shutil.disk_usage(Path.cwd())
    free_gib = usage.free / (1024 ** 3)

    print(f"Free disk space: {free_gib:.1f} GiB")

    if free_gib >= 2:
        print("PASS: At least 2 GiB of disk space is available.")
    else:
        print("WARN: Less than 2 GiB of disk space is available.")

    # Low disk space is a warning, not a hard failure.
    return True



def show_git_status():
    """Display the current Git branch and working-tree status."""
    if shutil.which("git") is None:
        print("Error: Git is not installed or not available on PATH.")
        return

    result = subprocess.run(
        ["git", "status", "--short", "--branch"],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        error = result.stderr.strip()
        print(f"Error: Unable to read Git status. {error}")
        return

    lines = result.stdout.splitlines()

    if not lines:
        print("Error: Git returned no status information.")
        return

    branch_line = lines[0]

    if branch_line.startswith("## "):
        branch_info = branch_line[3:]
    else:
        branch_info = branch_line
    branch = branch_info.split("...", 1)[0]
    print(f"Branch: {branch}")
    if len(lines) == 1:
        print("Working tree: clean")
    else:
        print("Working tree: changes detected")

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
    sys.exit(main())
