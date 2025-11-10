ChatDev Documentation
=====================

Welcome to ChatDev's documentation. ChatDev is a multi-agent framework for automated software development using Large Language Models.

.. image:: https://img.shields.io/badge/python-3.9+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python Version

.. image:: https://img.shields.io/badge/license-Apache%202.0-green.svg
   :target: https://github.com/OpenBMB/ChatDev/blob/main/LICENSE
   :alt: License

Overview
--------

ChatDev simulates a virtual software company where AI agents with different roles collaborate to design, develop, test, and document software applications. The system uses multiple LLM-powered agents that communicate and cooperate to complete the software development lifecycle.

Key Features
------------

* **Multi-Agent Collaboration**: 9 distinct AI roles working together
* **Automated Development Pipeline**: From requirements to deployment
* **Customizable Workflows**: JSON-based configuration system
* **Multiple Operating Modes**: Default, Art, Human-in-the-loop, Incremental
* **Version Control Integration**: Optional Git management
* **Web Interface**: Real-time visualization dashboard

Quick Start
-----------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/OpenBMB/ChatDev.git
   cd ChatDev

   # Install dependencies
   pip install -r requirements.txt

   # Set up environment
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY

Basic Usage
~~~~~~~~~~~

.. code-block:: bash

   python run.py --task "Create a calculator application" --name "Calculator"

With custom configuration:

.. code-block:: bash

   python run.py --task "Build a game" --name "Game" --config "Art" --model "GPT_4"

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   quickstart
   configuration
   usage
   examples

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/chatdev
   api/camel
   api/exceptions

.. toctree::
   :maxdepth: 2
   :caption: Development

   contributing
   testing
   architecture
   changelog

.. toctree::
   :maxdepth: 1
   :caption: Additional Information

   security
   license
   faq

API Reference
-------------

Core Modules
~~~~~~~~~~~~

.. autosummary::
   :toctree: _autosummary
   :recursive:

   chatdev.chat_chain
   chatdev.phase
   chatdev.chat_env
   chatdev.exceptions
   camel.agents
   camel.model_backend

Architecture
------------

ChatDev follows a modular architecture:

* **ChatChain**: Main orchestrator managing the development workflow
* **Phases**: Individual development stages (Analysis, Coding, Testing, etc.)
* **Agents**: LLM-powered entities with specific roles
* **ChatEnv**: Environment manager for code, documents, and state
* **CAMEL**: Underlying framework for agent communication

Development Workflow
~~~~~~~~~~~~~~~~~~~~

1. **Demand Analysis**: CEO and CPO discuss product requirements
2. **Language Selection**: Technical stack decision
3. **Coding**: Implementation by programmer agents
4. **Code Review**: Quality assurance and improvements
5. **Testing**: Bug detection and fixes
6. **Documentation**: User manuals and technical docs

Contributing
------------

We welcome contributions! Please see our `Contributing Guide <contributing.html>`_ for details on:

* Setting up development environment
* Code style and standards
* Testing requirements
* Pull request process

Support
-------

* **GitHub Issues**: `Report bugs or request features <https://github.com/OpenBMB/ChatDev/issues>`_
* **Documentation**: This site
* **Email**: contact@camel-ai.org

License
-------

ChatDev is licensed under the Apache License 2.0. See `LICENSE <license.html>`_ for details.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
