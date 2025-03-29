# e-cb: A Flexible Chatbot Framework

[![Template](https://img.shields.io/badge/Template-LINCC%20Frameworks%20Python%20Project%20Template-brightgreen)](https://lincc-ppt.readthedocs.io/en/latest/)
[![PyPI](https://img.shields.io/pypi/v/e-cb?color=blue&logo=pypi&logoColor=white)](https://pypi.org/project/e-cb/)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/VKU/e-cb/smoke-test.yml)](https://github.com/VKU/e-cb/actions/workflows/smoke-test.yml)
[![Codecov](https://codecov.io/gh/VKU/e-cb/branch/main/graph/badge.svg)](https://codecov.io/gh/VKU/e-cb)
[![Read The Docs](https://img.shields.io/readthedocs/e-cb)](https://e-cb.readthedocs.io/)
[![Benchmarks](https://img.shields.io/github/actions/workflow/status/VKU/e-cb/asv-main.yml?label=benchmarks)](https://VKU.github.io/e-cb/)

A flexible and extensible chatbot framework built with Python.

## Installation

### End Users

If you just want to use the chatbot framework in your project:

```bash
pip install e-cb
```

### For Developers

#### Prerequisites

Before installing any dependencies or writing code, it's highly recommended to create a virtual environment:

**Using conda (recommended)**:
```bash
conda create -n chatbot-env python=3.10
conda activate chatbot-env
```

**Using venv**:
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python -m venv venv
source venv/bin/activate
```

#### Setup for Development

1. Clone the repository:
```bash
git clone https://github.com/NickDuyH2K3/E-CB.git
cd e-cb
```

2. Run the appropriate setup script for your operating system:

**On Windows**:
```bash
.\setup_dev.bat
```

**On macOS/Linux**:
```bash
chmod +x ./.setup_dev.sh
./.setup_dev.sh
```

3. Install pandoc (needed for documentation generation):

**Using conda**:
```bash
conda install pandoc
```

**On Windows (without conda)**:
Download from [pandoc.org](https://pandoc.org/installing.html)

**On macOS**:
```bash
brew install pandoc
```

**On Linux**:
```bash
sudo apt-get install pandoc
```

## Usage

Basic usage example:


See the [documentation](https://e-cb.readthedocs.io/) for more detailed usage examples and API reference.

## Development

### Running Tests

```bash
pytest
```

### Building Documentation

```bash
cd docs
make html
```

The documentation will be available in `docs/_build/html`.

### Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality. They were automatically installed during the setup process and will run each time you attempt to commit changes.


## Project Origins

This project was automatically generated using the LINCC-Frameworks [python-project-template](https://github.com/lincc-frameworks/python-project-template). For more information about the project template, see the [documentation](https://lincc-ppt.readthedocs.io/en/latest/).