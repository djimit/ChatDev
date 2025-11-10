# Contributing to ChatDev

Thank you for your interest in contributing to ChatDev! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Community](#community)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment. We expect all contributors to:

- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- OpenAI API key (for testing)

### First Time Contributors

If you're new to open source, check out:
- [How to Contribute to Open Source](https://opensource.guide/how-to-contribute/)
- [First Contributions](https://github.com/firstcontributions/first-contributions)

Look for issues labeled `good first issue` or `help wanted`.

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/ChatDev.git
cd ChatDev
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

### 4. Set Up Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# (Optional) Run against all files
pre-commit run --all-files
```

### 5. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-api-key-here
```

### 6. Verify Setup

```bash
# Run tests to verify everything works
pytest

# Run a simple example
python run.py --task "Create a hello world program" --name "HelloWorld"
```

## Development Workflow

### 1. Create a Branch

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Or a bugfix branch
git checkout -b fix/issue-number-description
```

### 2. Make Changes

- Write clean, readable code
- Follow the coding standards (see below)
- Add tests for new features
- Update documentation as needed

### 3. Run Quality Checks

```bash
# Format code with Black
black chatdev camel tests

# Sort imports with isort
isort chatdev camel tests

# Run linters
flake8 chatdev camel
pylint chatdev camel

# Run type checker
mypy chatdev camel

# Run security checks
bandit -r chatdev camel
safety check
```

### 4. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test file
pytest tests/unit/test_chat_chain.py

# Run tests matching a pattern
pytest -k "test_configuration"
```

### 5. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "Add feature: detailed description"
```

**Commit Message Format:**
```
<type>: <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Example:
```
feat: Add custom exception classes for better error handling

- Created ChatDevError base exception
- Added ConfigurationError, PhaseExecutionError, and APIError
- Updated chat_chain.py to use new exceptions
- Added comprehensive unit tests

Closes #123
```

### 6. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line length**: 100 characters (enforced by Black)
- **Quotes**: Use double quotes for strings
- **Imports**: Sorted with isort (use `isort --profile black`)
- **Formatting**: Automatically formatted with Black

### Code Quality

- **Type hints**: Add type hints to all function signatures
- **Docstrings**: Use Google-style docstrings
- **Error handling**: Use custom exceptions from `chatdev.exceptions`
- **Logging**: Use structured logging with `structlog` (when available)

### Example Function

```python
from typing import List, Optional

def process_phase(
    phase_name: str,
    config: dict,
    max_retries: int = 3
) -> Optional[dict]:
    """Process a development phase with retry logic.

    Args:
        phase_name: Name of the phase to process
        config: Configuration dictionary for the phase
        max_retries: Maximum number of retry attempts

    Returns:
        Dictionary containing phase results, or None if failed

    Raises:
        PhaseExecutionError: If phase execution fails after retries
        ConfigurationError: If configuration is invalid

    Example:
        >>> result = process_phase("Coding", config_dict)
        >>> print(result["status"])
        "completed"
    """
    # Implementation here
    pass
```

## Testing

### Writing Tests

- Place unit tests in `tests/unit/`
- Place integration tests in `tests/integration/`
- Use descriptive test names: `test_<function>_<scenario>_<expected_result>`
- Use pytest fixtures from `tests/conftest.py`

### Test Structure

```python
import pytest
from chatdev.chat_chain import ChatChain

class TestChatChain:
    """Test suite for ChatChain class."""

    def test_init_with_valid_config(self, mock_config_dir):
        """Test that ChatChain initializes correctly with valid config."""
        chain = ChatChain(
            config_path=str(mock_config_dir / "ChatChainConfig.json"),
            # ...
        )
        assert chain.project_name == "TestProject"

    def test_init_with_missing_config_raises_error(self):
        """Test that missing config file raises ConfigurationError."""
        with pytest.raises(ConfigurationError):
            ChatChain(config_path="/nonexistent/config.json")
```

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test class
pytest tests/unit/test_chat_chain.py::TestChatChain

# Run tests in parallel
pytest -n auto

# Run tests with coverage
pytest --cov=chatdev --cov-report=html
```

## Documentation

### Code Documentation

- Add docstrings to all public functions, classes, and modules
- Use Google-style docstrings
- Include examples where helpful

### README and Wiki

- Update README.md for user-facing changes
- Add wiki pages for major features
- Include code examples and screenshots

### API Documentation

We use Sphinx for API documentation:

```bash
# Generate documentation
cd docs
make html

# View documentation
open _build/html/index.html
```

## Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Pre-commit hooks pass
- [ ] No merge conflicts with main branch

### PR Description

Include in your PR description:

1. **Summary**: What does this PR do?
2. **Motivation**: Why is this change needed?
3. **Changes**: List of specific changes made
4. **Testing**: How was this tested?
5. **Screenshots**: For UI changes
6. **Related Issues**: Link to related issues

### Review Process

1. Automated checks must pass (CI/CD)
2. At least one maintainer approval required
3. Address review feedback
4. Squash commits if requested
5. Maintainer will merge when approved

### After Merge

- Delete your feature branch
- Update your fork's main branch
- Celebrate! 🎉

## Community

### Getting Help

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and general discussion
- **Email**: contact@camel-ai.org

### Ways to Contribute

Not just code! You can also:

- Report bugs
- Suggest features
- Improve documentation
- Write tutorials or blog posts
- Help answer questions
- Review pull requests
- Share your generated projects

## Recognition

Contributors will be:
- Listed in the project's contributors page
- Mentioned in release notes (for significant contributions)
- Added to the README (for major contributions)

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

---

**Thank you for contributing to ChatDev! Your efforts help make automated software development better for everyone.** 🚀
