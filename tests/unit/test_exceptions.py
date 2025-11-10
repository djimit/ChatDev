"""
Unit tests for chatdev.exceptions module.
"""
import pytest
from chatdev.exceptions import (
    ChatDevError,
    ConfigurationError,
    PhaseExecutionError,
    APIError,
    EmployeeNotFoundError,
    FileOperationError,
    ValidationError,
    GitOperationError
)


class TestChatDevError:
    """Test the base ChatDevError exception."""

    def test_base_exception(self):
        """Test that ChatDevError can be raised and caught."""
        with pytest.raises(ChatDevError):
            raise ChatDevError("Test error")

    def test_error_message(self):
        """Test that error message is properly stored."""
        error = ChatDevError("Test error message")
        assert str(error) == "Test error message"


class TestConfigurationError:
    """Test the ConfigurationError exception."""

    def test_without_config_path(self):
        """Test error without config path."""
        error = ConfigurationError("Config error")
        assert "Config error" in str(error)
        assert error.config_path is None

    def test_with_config_path(self):
        """Test error with config path."""
        error = ConfigurationError("Config error", config_path="/path/to/config.json")
        assert "Config error" in str(error)
        assert "/path/to/config.json" in str(error)
        assert error.config_path == "/path/to/config.json"

    def test_inheritance(self):
        """Test that ConfigurationError inherits from ChatDevError."""
        assert issubclass(ConfigurationError, ChatDevError)


class TestPhaseExecutionError:
    """Test the PhaseExecutionError exception."""

    def test_without_details(self):
        """Test error without phase details."""
        error = PhaseExecutionError("Phase failed")
        assert "Phase failed" in str(error)
        assert error.phase_name is None
        assert error.phase_type is None

    def test_with_phase_name(self):
        """Test error with phase name."""
        error = PhaseExecutionError("Phase failed", phase_name="Coding")
        assert "Phase failed" in str(error)
        assert "Coding" in str(error)
        assert error.phase_name == "Coding"

    def test_with_all_details(self):
        """Test error with all details."""
        error = PhaseExecutionError(
            "Phase failed",
            phase_name="Coding",
            phase_type="SimplePhase"
        )
        assert "Phase failed" in str(error)
        assert "Coding" in str(error)
        assert "SimplePhase" in str(error)
        assert error.phase_name == "Coding"
        assert error.phase_type == "SimplePhase"


class TestAPIError:
    """Test the APIError exception."""

    def test_without_details(self):
        """Test error without API details."""
        error = APIError("API request failed")
        assert "API request failed" in str(error)

    def test_with_api_name(self):
        """Test error with API name."""
        error = APIError("Request failed", api_name="OpenAI")
        assert "Request failed" in str(error)
        assert "OpenAI" in str(error)

    def test_with_status_code(self):
        """Test error with status code."""
        error = APIError("Request failed", status_code=429)
        assert "Request failed" in str(error)
        assert "429" in str(error)

    def test_with_retry_count(self):
        """Test error with retry count."""
        error = APIError("Request failed", retry_count=3)
        assert "Request failed" in str(error)
        assert "3" in str(error)

    def test_with_all_details(self):
        """Test error with all details."""
        error = APIError(
            "Request failed",
            api_name="OpenAI",
            status_code=500,
            retry_count=3
        )
        assert "Request failed" in str(error)
        assert "OpenAI" in str(error)
        assert "500" in str(error)
        assert "3" in str(error)


class TestEmployeeNotFoundError:
    """Test the EmployeeNotFoundError exception."""

    def test_without_available_roles(self):
        """Test error without available roles list."""
        error = EmployeeNotFoundError("Programmer")
        assert "Programmer" in str(error)
        assert error.role_name == "Programmer"

    def test_with_available_roles(self):
        """Test error with available roles list."""
        available = ["CEO", "CTO", "Designer"]
        error = EmployeeNotFoundError("Programmer", available_roles=available)
        assert "Programmer" in str(error)
        assert "CEO" in str(error)
        assert error.available_roles == available


class TestFileOperationError:
    """Test the FileOperationError exception."""

    def test_without_details(self):
        """Test error without file details."""
        error = FileOperationError("File operation failed")
        assert "File operation failed" in str(error)

    def test_with_file_path(self):
        """Test error with file path."""
        error = FileOperationError("Operation failed", file_path="/path/to/file.txt")
        assert "Operation failed" in str(error)
        assert "/path/to/file.txt" in str(error)

    def test_with_operation(self):
        """Test error with operation type."""
        error = FileOperationError("Operation failed", operation="read")
        assert "Operation failed" in str(error)
        assert "read" in str(error)


class TestValidationError:
    """Test the ValidationError exception."""

    def test_without_details(self):
        """Test error without validation details."""
        error = ValidationError("Validation failed")
        assert "Validation failed" in str(error)

    def test_with_field_name(self):
        """Test error with field name."""
        error = ValidationError("Invalid value", field_name="age")
        assert "Invalid value" in str(error)
        assert "age" in str(error)

    def test_with_expected_type(self):
        """Test error with expected type."""
        error = ValidationError("Type mismatch", expected_type="int")
        assert "Type mismatch" in str(error)
        assert "int" in str(error)

    def test_with_actual_value(self):
        """Test error with actual value."""
        error = ValidationError("Invalid value", actual_value="invalid")
        assert "Invalid value" in str(error)
        assert "invalid" in str(error)


class TestGitOperationError:
    """Test the GitOperationError exception."""

    def test_without_details(self):
        """Test error without git details."""
        error = GitOperationError("Git operation failed")
        assert "Git operation failed" in str(error)

    def test_with_command(self):
        """Test error with git command."""
        error = GitOperationError("Operation failed", command="git add .")
        assert "Operation failed" in str(error)
        assert "git add ." in str(error)

    def test_with_stderr(self):
        """Test error with stderr output."""
        error = GitOperationError("Operation failed", stderr="fatal: not a git repository")
        assert "Operation failed" in str(error)
        assert "fatal: not a git repository" in str(error)

    def test_with_return_code(self):
        """Test error with return code."""
        error = GitOperationError("Operation failed", return_code=128)
        assert "Operation failed" in str(error)
        assert "128" in str(error)

    def test_with_all_details(self):
        """Test error with all details."""
        error = GitOperationError(
            "Operation failed",
            command="git commit",
            stderr="nothing to commit",
            return_code=1
        )
        assert "Operation failed" in str(error)
        assert "git commit" in str(error)
        assert "nothing to commit" in str(error)
        assert "1" in str(error)
