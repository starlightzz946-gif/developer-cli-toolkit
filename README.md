# Developer CLI Toolkit

A lightweight command-line toolkit for developers, built with Python. It provides system information, environment diagnostics, file listing, Git status checks, network utilities, TCP port scanning, and scan report exports.

## Features

- **System Information:** Display operating system, OS release, and CPU architecture.
- **Environment Diagnostics:** Check Python, Git, and available disk space.
- **File Listing:** Recursively list files while ignoring common generated directories.
- **Git Status:** Check the current branch and working-tree state.
- **DNS Lookup:** Resolve a hostname to its IP addresses.
- **TCP Connectivity Check:** Test whether a TCP connection can be established to a host and port.
- **TCP Port Scanner:** Scan a specified TCP port or range on an authorized host.
- **Service Labels:** Display common service names for selected port numbers.
- **Report Export:** Save scan results as JSON, text, or CSV files.
- **Automated Tests:** Test core commands and error-handling behavior using Python's `unittest` framework.

## Requirements

- Python 3.10 or newer
- Git installed for Git-related functionality and the Git diagnostic check

The toolkit uses Python's standard library for its core functionality.

## Installation

Clone the repository:

```bash
git clone https://github.com/starlightzz946-gif/developer-cli-toolkit.git
cd developer-cli-toolkit
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

Install the project in editable mode:

```bash
python -m pip install -e .
```

Verify the installation:

```bash
devtool --version
devtool --help
```

## Usage

### 1. System Information

Display basic information about the computer:

```bash
devtool system
```

The command reports the operating system, OS release, and system architecture.

### 2. Environment Diagnostics

Check the development environment:

```bash
devtool doctor
```

The diagnostic command checks Python, Git, and available disk space. Required-check failures are reported so you can identify potential environment problems.

### 3. List Files

List files recursively from a directory:

```bash
devtool files
```

Specify a different directory:

```bash
devtool files /path/to/directory
```

The file listing excludes common generated directories such as `.git`, `.venv`, `__pycache__`, and `.egg-info`.

### 4. Git Status

Check the current Git branch and working-tree state:

```bash
devtool git
```

The command reports an error if Git is unavailable or the current directory is not inside a Git repository.

### 5. DNS Lookup

Resolve a hostname:

```bash
devtool network example.com
```

The command displays the resolved IP addresses and handles DNS lookup failures.

### 6. TCP Connectivity Check

Test whether a TCP connection can be established to a host:

```bash
devtool network example.com --check
```

Specify a port:

```bash
devtool network example.com --check --port 443
```

The default connection-check port is `443`, and the connection attempt uses a short timeout.

A failed connection does not necessarily mean that a service is unavailable; firewalls, routing, and other network conditions can affect the result.

### 7. TCP Port Scanner

Scan a single TCP port on a host you own or have permission to test:

```bash
devtool scan 127.0.0.1 --ports 22
```

Scan a small range of ports:

```bash
devtool scan 127.0.0.1 --ports 20-23
```

Scan the default range of ports 1–1024:

```bash
devtool scan 127.0.0.1
```

The scanner reports ports where a TCP connection succeeds. Ports that are not reported as open are not necessarily confirmed closed; connection attempts can fail for several reasons.

#### Service Labels

The scanner displays common service labels for selected port numbers, including:

| Port | Common service label |
|---:|---|
| 22 | SSH |
| 53 | DNS |
| 80 | HTTP |
| 443 | HTTPS |
| 3306 | MySQL |

These labels are conventional associations based on port numbers. They do not verify which software is actually running on a port. Ports without a listed association are labelled `Unknown`.

#### Exporting Scan Reports

Scan results can be saved in JSON, text, or CSV format using `--output` and `--format`.

**JSON format**

```bash
devtool scan 127.0.0.1 --ports 20-23 --output scan.json --format json
```

JSON stores structured scan information, including the hostname, scanned ports, and open ports with their service labels.

**Text format**

```bash
devtool scan 127.0.0.1 --ports 20-23 --output scan.txt --format text
```

Text format creates a human-readable summary of the scan, including the scanned ports and open-port count.

**CSV format**

```bash
devtool scan 127.0.0.1 --ports 20-23 --output scan.csv --format csv
```

CSV format creates a tabular report that can be opened in spreadsheet applications such as Excel or imported into other data-analysis tools.

The CSV report contains these columns:

| Column | Description |
|---|---|
| `hostname` | Host that was scanned |
| `port` | TCP port number |
| `service` | Common service label associated with the port |
| `status` | `OPEN` or `CLOSED` according to the scanner's connection result |

The CSV report includes one row for each scanned port.

**Report options**

- `--output` specifies where the report is saved.
- `--format` selects `json`, `text`, or `csv`.
- If `--format` is omitted, JSON is the default format.
- If `--output` is omitted, the scanner does not save a report file.

The scanner reports an error if it cannot write the requested report.

## Running the Tests

Run the complete automated test suite from the project root:

```bash
python -m unittest discover -s tests -v
```

The test suite covers command behavior, environment diagnostics, file listing, Git checks, DNS resolution, TCP connectivity, port-range validation, port scanning, service labels, report generation, and relevant error cases.

Tests use mocks where appropriate so network-related behavior can be tested without relying on actual remote services.

## Project Structure

```text
developer-cli-toolkit/
├── src/
│   └── devtool/
│       ├── __init__.py
│       └── cli.py
├── tests/
│   └── test_cli.py
├── .gitignore
├── pyproject.toml
└── README.md
```

- `src/devtool/cli.py` contains the CLI commands and their implementations.
- `tests/test_cli.py` contains automated tests.
- `pyproject.toml` defines the project configuration and command-line entry point.
- `README.md` documents installation, usage, and features.

## Responsible Use

Use network diagnostic and scanning features only on systems you own or have explicit authorization to test.

This toolkit performs basic TCP connection checks. It is intended for learning, development, and authorized troubleshooting; it is not a comprehensive vulnerability scanner or a guarantee of service identification.

## Technology

- Python
- `argparse` for command-line argument parsing
- Python standard-library modules for system information, filesystem operations, Git integration, DNS lookups, TCP connections, JSON, and CSV
- `unittest` and `unittest.mock` for automated testing

## License

No license has been specified yet. If you intend to distribute or accept contributions to this project, consider adding an appropriate open-source license.