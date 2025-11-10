Exceptions Reference
====================

ChatDev uses a hierarchy of custom exceptions for better error handling.

Exception Hierarchy
-------------------

.. code-block:: text

   ChatDevError (base)
   ├── ConfigurationError
   ├── PhaseExecutionError
   ├── APIError
   ├── EmployeeNotFoundError
   ├── FileOperationError
   ├── ValidationError
   └── GitOperationError

Exception Classes
-----------------

.. autoclass:: chatdev.exceptions.ChatDevError
   :members:
   :show-inheritance:

.. autoclass:: chatdev.exceptions.ConfigurationError
   :members:
   :show-inheritance:

.. autoclass:: chatdev.exceptions.PhaseExecutionError
   :members:
   :show-inheritance:

.. autoclass:: chatdev.exceptions.APIError
   :members:
   :show-inheritance:

.. autoclass:: chatdev.exceptions.EmployeeNotFoundError
   :members:
   :show-inheritance:

.. autoclass:: chatdev.exceptions.FileOperationError
   :members:
   :show-inheritance:

.. autoclass:: chatdev.exceptions.ValidationError
   :members:
   :show-inheritance:

.. autoclass:: chatdev.exceptions.GitOperationError
   :members:
   :show-inheritance:

Usage Examples
--------------

Configuration Errors
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from chatdev.exceptions import ConfigurationError

   try:
       load_config("missing_file.json")
   except ConfigurationError as e:
       print(f"Config error: {e}")
       print(f"Config path: {e.config_path}")

Phase Execution Errors
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from chatdev.exceptions import PhaseExecutionError

   try:
       execute_phase("UnknownPhase")
   except PhaseExecutionError as e:
       print(f"Phase error: {e}")
       print(f"Phase name: {e.phase_name}")
       print(f"Phase type: {e.phase_type}")

API Errors
~~~~~~~~~~

.. code-block:: python

   from chatdev.exceptions import APIError

   try:
       call_openai_api()
   except APIError as e:
       print(f"API error: {e}")
       print(f"Status code: {e.status_code}")
       print(f"Retry count: {e.retry_count}")
