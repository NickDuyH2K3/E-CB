# e-cb: A Flexible Chatbot Framework

[![Template](https://img.shields.io/badge/Template-LINCC%20Frameworks%20Python%20Project%20Template-brightgreen)](https://lincc-ppt.readthedocs.io/en/latest/)
[![PyPI](https://img.shields.io/pypi/v/e-cb?color=blue&logo=pypi&logoColor=white)](https://pypi.org/project/e-cb/)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/VKU/e-cb/smoke-test.yml)](https://github.com/VKU/e-cb/actions/workflows/smoke-test.yml)
[![Codecov](https://codecov.io/gh/VKU/e-cb/branch/main/graph/badge.svg)](https://codecov.io/gh/VKU/e-cb)
[![Read The Docs](https://img.shields.io/readthedocs/e-cb)](https://e-cb.readthedocs.io/)
[![Benchmarks](https://img.shields.io/github/actions/workflow/status/VKU/e-cb/asv-main.yml?label=benchmarks)](https://VKU.github.io/e-cb/)

A flexible and extensible chatbot framework built with Python.

## Installation

### Quick Installation (End Users)

To use the framework in your project:

```bash
pip install e-cb
```

### Developer Installation

#### Step 1: Set Up a Virtual Environment

Choose one method:

**Option A: Using conda (recommended)**
```bash
conda create -n chatbot-env python=3.10
conda activate chatbot-env
```

**Option B: Using venv**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

#### Step 2: Get the Code

Clone the repository:
```bash
git clone https://github.com/NickDuyH2K3/E-CB.git
cd e-cb
```

#### Step 3: Install Dependencies

Run the appropriate setup script:

```bash
# Windows
.\setup_dev.bat

# macOS/Linux
chmod +x ./.setup_dev.sh
./.setup_dev.sh
```

#### Step 4: Install Documentation Tools

Install pandoc for generating documentation:

```bash
# Using conda
conda install pandoc

# macOS
brew install pandoc

# Windows (without conda)
# Download from https://pandoc.org/installing.html

# Linux
sudo apt-get install pandoc
```

## Usage

Basic usage example:

```python
from e_cb import ChatBot

# Initialize a simple chatbot
bot = ChatBot()

# Get a response
response = bot.get_response("Hello, how are you?")
print(response)
```

See the [documentation](https://e-cb.readthedocs.io/) for more detailed examples and API reference.

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

This project uses pre-commit hooks to ensure code quality. They were automatically installed during the setup process and will run each time you commit changes.

## Project Origins

This project was automatically generated using the LINCC-Frameworks [python-project-template](https://github.com/lincc-frameworks/python-project-template). For more information about the project template, see the [documentation](https://lincc-ppt.readthedocs.io/en/latest/).