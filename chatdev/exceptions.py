# =========== Copyright 2023 @ CAMEL-AI.org. All Rights Reserved. ===========
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =========== Copyright 2023 @ CAMEL-AI.org. All Rights Reserved. ===========
"""
Custom exception classes for ChatDev framework.

This module provides a hierarchy of exception classes for better error handling
and debugging throughout the ChatDev application.
"""


class ChatDevError(Exception):
    """Base exception class for all ChatDev errors.

    All custom exceptions in ChatDev should inherit from this class.
    """
    pass


class ConfigurationError(ChatDevError):
    """Exception raised for configuration-related errors.

    This includes:
    - Missing configuration files
    - Invalid JSON in configuration files
    - Missing required configuration keys
    - Invalid configuration values

    Args:
        message: Human-readable error message
        config_path: Optional path to the problematic configuration file
    """

    def __init__(self, message: str, config_path: str = None):
        self.config_path = config_path
        if config_path:
            message = f"{message} (config: {config_path})"
        super().__init__(message)


class PhaseExecutionError(ChatDevError):
    """Exception raised when a phase fails to execute properly.

    This includes:
    - Phase not found or not implemented
    - Phase execution timeout
    - Invalid phase configuration
    - Agent conversation failures

    Args:
        message: Human-readable error message
        phase_name: Name of the phase that failed
        phase_type: Type of phase (SimplePhase, ComposedPhase, etc.)
    """

    def __init__(self, message: str, phase_name: str = None, phase_type: str = None):
        self.phase_name = phase_name
        self.phase_type = phase_type
        details = []
        if phase_name:
            details.append(f"phase: {phase_name}")
        if phase_type:
            details.append(f"type: {phase_type}")
        if details:
            message = f"{message} ({', '.join(details)})"
        super().__init__(message)


class APIError(ChatDevError):
    """Exception raised for API-related errors.

    This includes:
    - OpenAI API failures
    - Network connection issues
    - Rate limiting
    - Invalid API keys
    - API timeout

    Args:
        message: Human-readable error message
        api_name: Name of the API (e.g., 'OpenAI')
        status_code: HTTP status code if applicable
        retry_count: Number of retries attempted
    """

    def __init__(
        self,
        message: str,
        api_name: str = None,
        status_code: int = None,
        retry_count: int = None
    ):
        self.api_name = api_name
        self.status_code = status_code
        self.retry_count = retry_count
        details = []
        if api_name:
            details.append(f"api: {api_name}")
        if status_code:
            details.append(f"status: {status_code}")
        if retry_count is not None:
            details.append(f"retries: {retry_count}")
        if details:
            message = f"{message} ({', '.join(details)})"
        super().__init__(message)


class EmployeeNotFoundError(ChatDevError):
    """Exception raised when a required employee/agent is not found.

    Args:
        role_name: Name of the missing role
        available_roles: List of available roles
    """

    def __init__(self, role_name: str, available_roles: list = None):
        self.role_name = role_name
        self.available_roles = available_roles
        message = f"Employee '{role_name}' not found in ChatEnv"
        if available_roles:
            message += f". Available roles: {', '.join(available_roles)}"
        super().__init__(message)


class FileOperationError(ChatDevError):
    """Exception raised for file operation errors.

    This includes:
    - File not found
    - Permission denied
    - Invalid file format
    - Disk space issues

    Args:
        message: Human-readable error message
        file_path: Path to the problematic file
        operation: Type of operation (read, write, delete, etc.)
    """

    def __init__(self, message: str, file_path: str = None, operation: str = None):
        self.file_path = file_path
        self.operation = operation
        details = []
        if file_path:
            details.append(f"file: {file_path}")
        if operation:
            details.append(f"operation: {operation}")
        if details:
            message = f"{message} ({', '.join(details)})"
        super().__init__(message)


class ValidationError(ChatDevError):
    """Exception raised for data validation errors.

    This includes:
    - Invalid input data
    - Type mismatches
    - Out of range values
    - Missing required fields

    Args:
        message: Human-readable error message
        field_name: Name of the invalid field
        expected_type: Expected data type or format
        actual_value: The actual invalid value
    """

    def __init__(
        self,
        message: str,
        field_name: str = None,
        expected_type: str = None,
        actual_value: any = None
    ):
        self.field_name = field_name
        self.expected_type = expected_type
        self.actual_value = actual_value
        details = []
        if field_name:
            details.append(f"field: {field_name}")
        if expected_type:
            details.append(f"expected: {expected_type}")
        if actual_value is not None:
            details.append(f"got: {actual_value}")
        if details:
            message = f"{message} ({', '.join(details)})"
        super().__init__(message)


class GitOperationError(ChatDevError):
    """Exception raised for git operation failures.

    Args:
        message: Human-readable error message
        command: Git command that failed
        stderr: Error output from git command
        return_code: Git command return code
    """

    def __init__(
        self,
        message: str,
        command: str = None,
        stderr: str = None,
        return_code: int = None
    ):
        self.command = command
        self.stderr = stderr
        self.return_code = return_code
        details = []
        if command:
            details.append(f"command: {command}")
        if return_code is not None:
            details.append(f"exit code: {return_code}")
        if details:
            message = f"{message} ({', '.join(details)})"
        if stderr:
            message += f"\nGit error: {stderr}"
        super().__init__(message)
