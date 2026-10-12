# Developer CLI Toolkit

A lightweight command-line toolkit for developers, built with Python.

## Features

- Display application version and help.
- Inspect operating system, release, architecture, and Python version.
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