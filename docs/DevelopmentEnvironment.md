# Development Environment

## Introduction

This page describes how to set up a development environment, and other
information useful for developers to be aware of.

## Prerequisites

The following instructions assume that "pyenv" and "pyenv-virtualenv" are
installed to enable the setup of an isolated Python environment.

See the following for setup instructions:

* https://github.com/pyenv/pyenv
* https://github.com/pyenv/pyenv-virtualenv

Once "pyenv" and "pyenv-virtualenv" have been installed, install Python 3.8.2:

```
> pyenv install 3.9.0
```

## Installation for development

1) Clone the "whpool" Git repository:

```
> git clone git@github.com:umd-lib/whpool.git
```

2) Switch to the "whpool" directory:

```
> cd whpool
```

3) Set up the virtual environment:

```
> pyenv virtualenv 3.9.0 whpool
> pyenv shell whpool
```

4) Run "pip install", including the "dev" and "test" dependencies:

```
> pip install -e .[dev,test]
```

## Running the tests

```
> pytest
```

**Note:** To restrict pytest test discovery to just the "tests" directory, run

```
> pytest tests
```

This can speed up pytest if you have "mbox" directories (or the output of the
extraction scripts in the directory).

## Code Style

Application code style should generally conform to the guidelines in
[PEP 8](https://www.python.org/dev/peps/pep-0008/). The "pycodestyle" tool
to check compliance with the guidelines can be run using:

```
> pycodestyle .
```

## Python Type Hinting

The application uses Python type hinting (see
[PEP 484](https://www.python.org/dev/peps/pep-0484/)) to document class and
method signatures.

The "mypy" tool can be used to assess issues with the type hinting:

```
> mypy whpool --strict --show-error-codes
```
