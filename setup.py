#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup script for ChatDev package."""

from pathlib import Path
from setuptools import setup, find_packages

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = (this_directory / "requirements.txt").read_text(encoding="utf-8").splitlines()
requirements = [req.strip() for req in requirements if req.strip() and not req.startswith("#")]

dev_requirements = (this_directory / "requirements-dev.txt").read_text(encoding="utf-8").splitlines()
dev_requirements = [
    req.strip()
    for req in dev_requirements
    if req.strip() and not req.startswith("#") and not req.startswith("-r")
]

setup(
    name="chatdev",
    version="1.0.0",
    author="CAMEL-AI.org",
    author_email="contact@camel-ai.org",
    description="Multi-agent framework for automated software development using Large Language Models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/OpenBMB/ChatDev",
    project_urls={
        "Documentation": "https://github.com/OpenBMB/ChatDev/wiki",
        "Source": "https://github.com/OpenBMB/ChatDev",
        "Bug Tracker": "https://github.com/OpenBMB/ChatDev/issues",
    },
    packages=find_packages(exclude=["tests", "tests.*", "WareHouse", "WareHouse.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development",
        "Topic :: Software Development :: Code Generators",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
        "test": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
        ],
        "docs": [
            "sphinx>=7.2.6",
            "sphinx-rtd-theme>=2.0.0",
            "sphinx-autodoc-typehints>=1.25.2",
        ],
    },
    entry_points={
        "console_scripts": [
            "chatdev=run:main",
        ],
    },
    include_package_data=True,
    package_data={
        "chatdev": ["py.typed"],
        "": ["*.json", "*.md"],
    },
    keywords=[
        "artificial-intelligence",
        "multi-agent",
        "software-development",
        "llm",
        "openai",
        "automation",
        "code-generation",
        "chatgpt",
    ],
    license="Apache-2.0",
    zip_safe=False,
)
