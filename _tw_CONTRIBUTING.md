# Contributing to DocFlow

First off, thank you for considering contributing to DocFlow! It's people like you that make DocFlow such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples to demonstrate the steps**
- **Describe the behavior you observed and expected**
- **Include screenshots if helpful**

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Use a clear and descriptive title**
- **Provide a step-by-step description of the suggested enhancement**
- **Provide specific examples to demonstrate the steps**
- **Describe the current behavior and explain the expected behavior**
- **Explain why this enhancement would be useful**

### Pull Requests

- Fill in the required template
- Do not include issue numbers in the PR title
- Include screenshots and animated GIFs in your pull request whenever possible
- Follow the Python style guide
- Include tests for new features
- Update documentation for changed functionality

## Development Setup

### Prerequisites

- Python 3.9 or higher
- pip or uv package manager
- Git

### Setup Steps

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/yourusername/docflow.git
   cd docflow
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Run tests:
   ```bash
   pytest
   ```

5. Run linting:
   ```bash
   ruff check docflow
   mypy docflow
   ```

## Style Guidelines

### Git Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` A new feature
- `fix:` A bug fix
- `docs:` Documentation only changes
- `style:` Changes that do not affect the meaning of the code
- `refactor:` A code change that neither fixes a bug nor adds a feature
- `perf:` A code change that improves performance
- `test:` Adding missing tests or correcting existing tests
- `chore:` Changes to the build process or auxiliary tools

### Python Style Guide

- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) for formatting
- Use type hints for all public functions
- Write docstrings for all public modules, functions, classes, and methods

### Documentation Style Guide

- Use [Markdown](https://daringfireball.net/projects/markdown/) for documentation
- Reference functions and classes with backticks
- Include code examples where appropriate

## Project Structure

```
docflow/
├── docflow/                 # Main package
│   ├── core/               # Core conversion engine
│   │   ├── converters/     # Format converters
│   │   ├── extractors/     # Metadata extractors
│   │   └── processors/     # Post-processors
│   ├── cli/                # CLI interface
│   ├── config/             # Configuration
│   └── utils/              # Utility functions
├── tests/                  # Test suite
├── docs/                   # Documentation
└── pyproject.toml          # Project configuration
```

## Adding a New Converter

1. Create a new file in `docflow/core/converters/`
2. Inherit from `BaseConverter`
3. Implement the `convert` method
4. Add tests in `tests/`
5. Update the converter registry in `docflow/core/converter.py`
6. Update documentation

## Questions?

Feel free to open an issue with the "question" label, or reach out to the maintainers.

Thank you for your contributions! 🎉
