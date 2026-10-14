# Developer CLI Toolkit

A lightweight command-line toolkit for developers, built with Python.

## Features
- Display application version and help.
- Inspect operating system, release, architecture, and Python version.
- Check Python version, Git availability, and available disk space.
- List files recursively while excluding common generated directories.
- Inspect Git branch and working-tree status.
- Return meaningful exit codes from environment checks.
- Automated tests using Python's built-in `unittest` framework.
- Installable CLI command through Python packaging.

## Requirements

- Python 3.10 or newer
- pip

## Installation

Clone this repository and enter its directory:

```bash
git clone https://github.com/starlightzz946-gif/developer-cli-toolkit.git
cd developer-cli-toolkit
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the project:

```bash
python -m pip install -e .
```

## Usage

Display the version:

```bash
devtool --version
```

Display system information:

```bash
devtool system
```


### Check Git repository status

Display the current branch and whether the working tree is clean:

```bash
devtool git
```

Example output:

```text
Branch: main
Working tree: clean
```

If there are modified or untracked files, the command reports that changes were detected.

The command also reports an error if Git is unavailable or the current directory is not inside a Git repository.

### Resolve a hostname

Look up IP addresses associated with a hostname:

```bash
devtool network example.com
```

The command displays the unique IP addresses returned by the system's name-resolution service. A hostname may resolve to multiple IPv4 or IPv6 addresses.

If name resolution fails, the command displays an error and returns exit code `1`.

**Exit codes**

- `0` — hostname resolution succeeded.
- `1` — hostname resolution failed or returned no addresses.

Successful DNS resolution does not guarantee that a website is reachable or accepting connections.

### List files

List files recursively in the current directory:

```bash
devtool files
```

Specify a directory:

```bash
devtool files ./src
```

The command excludes common generated directories, including `.git`, `.venv`, `__pycache__`, and package metadata directories.

### Check your development environment

Run the environment checks:

```bash
devtool doctor
```

The command checks:

- Whether Python 3.10 or newer is installed.
- Whether Git is available and its version can be retrieved.
- Whether at least 2 GiB of disk space is available.

Low disk space produces a warning rather than failing the command.

**Exit codes**

| Exit code | Meaning |
|---|---|
| `0` | All required checks passed. |
| `1` | At least one required check failed. |

These exit codes allow shell scripts and other automation to determine whether the environment checks succeeded.


Display help:

```bash
devtool --help
```

## Tests

Run the automated test suite:

```bash
python -m unittest discover -s tests -v
```

## Technology

- Python
- argparse
- platform
- unittest
- setuptools

## License

This project is currently an early development release. A license will be added when one is selected.