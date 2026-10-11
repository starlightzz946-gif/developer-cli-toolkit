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


### Check your development environment

```bash
devtool doctor
```

Checks:
- Python version compatibility (Python 3.10 or newer)
- Git availability and version
- Available disk space

The command reports a PASS or WARN status for each diagnostic.


### List files in a directory

List files recursively in the current directory:

```bash
devtool files
```

Search a specific directory:

```bash
devtool files ./src
```

The command skips generated directories such as `.git`, `.venv`, `__pycache__`, and `*.egg-info`.


Display system information:

```bash
devtool system
```

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