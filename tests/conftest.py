"""
Pytest configuration and fixtures for ChatDev tests.

This module provides shared fixtures and configuration for all tests.
"""
import json
import os
import tempfile
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, MagicMock

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_config_dir(temp_dir):
    """Create a temporary directory with mock configuration files."""
    config_dir = temp_dir / "CompanyConfig" / "Test"
    config_dir.mkdir(parents=True)

    # Create mock ChatChainConfig.json
    chat_chain_config = {
        "chain": [
            {
                "phase": "DemandAnalysis",
                "phaseType": "SimplePhase",
                "max_turn_step": 2,
                "need_reflect": "False"
            }
        ],
        "recruitments": ["Chief Executive Officer", "Chief Product Officer"],
        "clear_structure": "True",
        "gui_design": "False",
        "git_management": "False",
        "incremental_develop": "False",
        "self_improve": "False"
    }

    with open(config_dir / "ChatChainConfig.json", "w") as f:
        json.dump(chat_chain_config, f, indent=2)

    # Create mock PhaseConfig.json
    phase_config = {
        "DemandAnalysis": {
            "assistant_role_name": "Chief Product Officer",
            "user_role_name": "Chief Executive Officer",
            "phase_prompt": ["Test phase prompt"]
        }
    }

    with open(config_dir / "PhaseConfig.json", "w") as f:
        json.dump(phase_config, f, indent=2)

    # Create mock RoleConfig.json
    role_config = {
        "Chief Executive Officer": ["You are a CEO"],
        "Chief Product Officer": ["You are a CPO"],
        "Counselor": ["You are a counselor"]
    }

    with open(config_dir / "RoleConfig.json", "w") as f:
        json.dump(role_config, f, indent=2)

    return config_dir


@pytest.fixture
def mock_openai_response():
    """Create a mock OpenAI API response."""
    return {
        "id": "chatcmpl-test123",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "gpt-3.5-turbo",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Test response content"
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        }
    }


@pytest.fixture
def mock_openai_client(mock_openai_response, monkeypatch):
    """Mock the OpenAI API client."""
    mock_client = MagicMock()
    mock_client.ChatCompletion.create.return_value = mock_openai_response

    # Also mock the new API style
    mock_completion = MagicMock()
    mock_completion.create.return_value = mock_openai_response
    mock_client.chat.completions = mock_completion

    monkeypatch.setattr("openai.ChatCompletion", mock_client.ChatCompletion)
    monkeypatch.setattr("openai.chat.completions", mock_completion)

    return mock_client


@pytest.fixture
def sample_task_prompt():
    """Provide a sample task prompt for testing."""
    return "Create a simple calculator application"


@pytest.fixture
def sample_project_name():
    """Provide a sample project name for testing."""
    return "TestCalculator"


@pytest.fixture
def sample_org_name():
    """Provide a sample organization name for testing."""
    return "TestOrg"


@pytest.fixture
def mock_warehouse_dir(temp_dir):
    """Create a mock WareHouse directory."""
    warehouse = temp_dir / "WareHouse"
    warehouse.mkdir()
    return warehouse


@pytest.fixture(autouse=True)
def setup_test_env(temp_dir, monkeypatch):
    """Set up test environment variables and paths."""
    # Set fake API key for testing
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key-1234567890")

    # Ensure we're using the temp directory
    yield

    # Cleanup is handled by temp_dir fixture


@pytest.fixture
def mock_git_repo(temp_dir):
    """Create a mock git repository for testing."""
    import subprocess

    repo_dir = temp_dir / "test_repo"
    repo_dir.mkdir()

    # Initialize git repo
    subprocess.run(["git", "init"], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_dir,
        check=True,
        capture_output=True
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_dir,
        check=True,
        capture_output=True
    )

    # Create initial commit
    test_file = repo_dir / "README.md"
    test_file.write_text("# Test Repository")
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=repo_dir,
        check=True,
        capture_output=True
    )

    return repo_dir


@pytest.fixture
def mock_phase():
    """Create a mock Phase instance."""
    phase = Mock()
    phase.phase_name = "TestPhase"
    phase.execute = Mock(return_value=None)
    return phase


@pytest.fixture
def mock_chat_env():
    """Create a mock ChatEnv instance."""
    env = Mock()
    env.env_dict = {
        "directory": "/tmp/test",
        "task_prompt": "Test task"
    }
    env.codes = Mock()
    env.codes.version = 0
    env.config = Mock()
    env.config.clear_structure = True
    env.config.git_management = False
    env.exist_employee = Mock(return_value=True)
    env.recruit = Mock()
    env.write_meta = Mock()
    return env


# Markers for different test categories
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "requires_api: mark test as requiring API access"
    )
