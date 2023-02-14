# Development Environment

## Introduction

This page describes how to set up a development environment, and other
information useful for developers to be aware of.

## Prerequisites

The following instructions assume that "pyenv" is installed to enable
the setup of an isolated Python environment.

See the following for setup instructions:

* <https://github.com/pyenv/pyenv>

Once "pyenv" have been installed, install Python 3.9:

```bash
pyenv install 3.9
```

This should download and install the latest version of Python 3.9.

## Installation for development

1. Clone the "whpool" Git repository:
    ```bash
    git clone git@github.com:umd-lib/whpool.git
    ```
2. Switch to the "whpool" directory:
    ```bash
    cd whpool
    ```
3. Verify that the Python version is 3.9:
    ```bash
    pyenv version
    ```
4. Create and activate the virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
5. Install all dependencies and configure the `whpool` entrypoint:
   ```bash
   pip install -r requirements.dev.txt -e .
   ```
6. Create an ".env" file to access the Email server with the following:
   ```ini
   user='[email account]'
   password='[account's password]'
   host='[host]]'
   port='[port]'
   ```

## Running the tests

```bash
pytest
```

**Note:** To restrict pytest test discovery to just the "tests" directory, run

```bash
pytest tests
```

This can speed up pytest if you have "mbox" directories (or the output of the
extraction scripts in the directory).

## Code Style

Application code style should generally conform to the guidelines in [PEP 8]. The
"pycodestyle" tool to check compliance with the guidelines can be run using:

```bash
pycodestyle .
```

## Python Type Hinting

The application uses Python type hinting (see [PEP 484]) to document class and
method signatures.

The "mypy" tool can be used to assess issues with the type hinting:

```bash
mypy whpool --strict --show-error-codes
```

[PEP 8]: https://www.python.org/dev/peps/pep-0008/
[PEP 484]: https://www.python.org/dev/peps/pep-0484/
