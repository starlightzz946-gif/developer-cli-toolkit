
import argparse
import platform


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

    args = parser.parse_args()

    if args.command == "system":
        show_system_info()
    elif args.command is None:
        parser.print_help()


if __name__ == "__main__":
    main()
