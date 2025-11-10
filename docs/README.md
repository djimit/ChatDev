# ChatDev Documentation

This directory contains the Sphinx documentation for ChatDev.

## Building the Documentation

### Prerequisites

Install documentation dependencies:

```bash
pip install -r requirements-dev.txt
```

Or install just the docs dependencies:

```bash
pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints myst-parser
```

### Build HTML Documentation

```bash
cd docs
make html
```

The built documentation will be in `docs/_build/html/`. Open `index.html` in your browser:

```bash
# On macOS
open _build/html/index.html

# On Linux
xdg-open _build/html/index.html

# On Windows
start _build/html/index.html
```

### Other Output Formats

```bash
# PDF (requires LaTeX)
make latexpdf

# EPUB
make epub

# Plain text
make text

# Man pages
make man
```

### Clean Build Files

```bash
make clean
```

## Documentation Structure

```
docs/
├── conf.py              # Sphinx configuration
├── index.rst            # Main documentation page
├── Makefile            # Build commands
├── api/                # API reference documentation
│   ├── chatdev.rst
│   ├── camel.rst
│   └── exceptions.rst
└── _build/             # Generated documentation (gitignored)
```

## Writing Documentation

### reStructuredText (.rst)

Sphinx uses reStructuredText format by default:

```rst
Section Title
=============

Subsection
----------

* Bullet points
* Another point

.. code-block:: python

   # Python code example
   def hello():
       print("Hello, World!")
```

### Markdown (.md)

You can also use Markdown thanks to MyST parser:

```markdown
# Section Title

## Subsection

- Bullet points
- Another point

```python
# Python code example
def hello():
    print("Hello, World!")
```
```

### Docstrings

Use Google-style docstrings in Python code:

```python
def example_function(arg1: str, arg2: int) -> bool:
    """Brief description of the function.

    Longer description explaining what the function does,
    how it works, and any important details.

    Args:
        arg1: Description of first argument
        arg2: Description of second argument

    Returns:
        Description of return value

    Raises:
        ValueError: When input is invalid
        TypeError: When argument type is wrong

    Example:
        >>> result = example_function("test", 42)
        >>> print(result)
        True
    """
    return True
```

## Auto-generated Documentation

Sphinx automatically generates API documentation from docstrings using the `autodoc` extension.

To document a new module:

1. Add docstrings to your Python code
2. Add the module to the appropriate `.rst` file in `api/`
3. Rebuild the documentation

## Live Preview

For continuous rebuild during development:

```bash
pip install sphinx-autobuild
sphinx-autobuild docs docs/_build/html
```

This will:
- Watch for changes in the `docs/` directory
- Automatically rebuild documentation
- Serve it at http://127.0.0.1:8000
- Auto-reload your browser

## Troubleshooting

### Module Import Errors

If Sphinx can't find your modules:

```bash
# Make sure the project root is in PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
cd docs
make html
```

### Missing Dependencies

If you see import errors for documentation dependencies:

```bash
pip install -r requirements-dev.txt
```

### Clean and Rebuild

If you encounter caching issues:

```bash
cd docs
make clean
make html
```

## Contributing to Documentation

1. Follow the existing structure and style
2. Add docstrings to all public APIs
3. Include code examples where helpful
4. Build and review documentation locally before submitting PR
5. Check for warnings during build: `make html`

## Resources

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [reStructuredText Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
- [MyST Parser](https://myst-parser.readthedocs.io/)
- [Read the Docs](https://readthedocs.org/)
