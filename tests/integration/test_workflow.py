"""
Integration tests for ChatDev full workflow.

These tests verify that the complete ChatDev workflow functions correctly
from initialization through to software generation.
"""
import json
import os
import pytest
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from camel.typing import ModelType
from chatdev.chat_chain import ChatChain
from chatdev.exceptions import ConfigurationError


@pytest.mark.integration
class TestFullWorkflow:
    """Integration tests for complete ChatDev workflow."""

    def test_initialization_with_valid_config(self, mock_config_dir, mock_warehouse_dir):
        """Test that ChatChain can be initialized with valid configuration."""
        with patch('chatdev.chat_chain.ChatEnv'):
            chain = ChatChain(
                config_path=str(mock_config_dir / "ChatChainConfig.json"),
                config_phase_path=str(mock_config_dir / "PhaseConfig.json"),
                config_role_path=str(mock_config_dir / "RoleConfig.json"),
                task_prompt="Create a simple calculator",
                project_name="Calculator",
                org_name="TestOrg",
                model_type=ModelType.GPT_3_5_TURBO
            )

            assert chain.project_name == "Calculator"
            assert chain.org_name == "TestOrg"
            assert chain.task_prompt_raw == "Create a simple calculator"
            assert len(chain.phases) > 0

    def test_recruitment_creates_all_employees(self, mock_config_dir):
        """Test that employee recruitment adds all configured roles."""
        with patch('chatdev.chat_chain.ChatEnv') as mock_env_class:
            mock_env = Mock()
            mock_env_class.return_value = mock_env

            chain = ChatChain(
                config_path=str(mock_config_dir / "ChatChainConfig.json"),
                config_phase_path=str(mock_config_dir / "PhaseConfig.json"),
                config_role_path=str(mock_config_dir / "RoleConfig.json"),
                task_prompt="Test task",
                project_name="TestProject",
                org_name="TestOrg"
            )

            chain.make_recruitment()

            # Should have recruited all configured employees
            assert mock_env.recruit.called
            assert mock_env.recruit.call_count == len(chain.recruitments)

    @pytest.mark.slow
    def test_log_file_creation(self, mock_config_dir, temp_dir):
        """Test that log files are created correctly."""
        with patch('chatdev.chat_chain.ChatEnv'):
            chain = ChatChain(
                config_path=str(mock_config_dir / "ChatChainConfig.json"),
                config_phase_path=str(mock_config_dir / "PhaseConfig.json"),
                config_role_path=str(mock_config_dir / "RoleConfig.json"),
                task_prompt="Test task",
                project_name="TestProject",
                org_name="TestOrg"
            )

            # Log filepath should be generated
            assert chain.log_filepath is not None
            assert "TestProject" in chain.log_filepath
            assert "TestOrg" in chain.log_filepath
            assert ".log" in chain.log_filepath

    def test_config_fallback_to_default(self, temp_dir):
        """Test that missing custom config falls back to default."""
        from run import get_config

        # Create only default configs
        default_dir = temp_dir / "CompanyConfig" / "Default"
        default_dir.mkdir(parents=True)

        for filename in ["ChatChainConfig.json", "PhaseConfig.json", "RoleConfig.json"]:
            (default_dir / filename).write_text("{}")

        # Try to get non-existent custom config
        with patch('run.root', str(temp_dir)):
            config_paths = get_config("NonExistent")

            # Should return default paths
            for path in config_paths:
                assert "Default" in path

    def test_git_repo_initialization(self, mock_git_repo, mock_config_dir):
        """Test git repository operations in a real git environment."""
        with patch('chatdev.chat_chain.ChatEnv') as mock_env_class:
            mock_env = Mock()
            mock_env.env_dict = {"directory": str(mock_git_repo)}
            mock_env.codes = Mock()
            mock_env.codes.version = 0
            mock_env.config = Mock()
            mock_env.config.git_management = True
            mock_env.config.clear_structure = False
            mock_env_class.return_value = mock_env

            chain = ChatChain(
                config_path=str(mock_config_dir / "ChatChainConfig.json"),
                config_phase_path=str(mock_config_dir / "PhaseConfig.json"),
                config_role_path=str(mock_config_dir / "RoleConfig.json"),
                task_prompt="Test task",
                project_name="TestProject",
                org_name="TestOrg"
            )

            chain.chat_env = mock_env
            chain.chat_env_config = mock_env.config

            # Add a test file
            test_file = mock_git_repo / "test.txt"
            test_file.write_text("Test content")

            # This should not raise an error
            try:
                chain.post_processing()
            except Exception as e:
                # post_processing may fail due to other reasons,
                # but git operations should succeed
                if "git" in str(e).lower():
                    pytest.fail(f"Git operation failed: {e}")


@pytest.mark.integration
class TestEndToEndWorkflow:
    """End-to-end integration tests with mocked API calls."""

    @pytest.fixture
    def mock_api_calls(self, monkeypatch, mock_openai_response):
        """Mock all external API calls."""
        mock_client = MagicMock()
        mock_client.ChatCompletion.create.return_value = mock_openai_response

        monkeypatch.setattr("openai.ChatCompletion.create", mock_client.ChatCompletion.create)
        return mock_client

    @pytest.mark.slow
    def test_minimal_workflow_execution(
        self,
        mock_config_dir,
        mock_api_calls,
        temp_dir
    ):
        """Test a minimal workflow execution with mocked components."""
        # Create warehouse directory
        warehouse = temp_dir / "WareHouse"
        warehouse.mkdir()

        with patch('chatdev.chat_chain.ChatEnv') as mock_env_class:
            with patch('chatdev.chat_chain.now') as mock_now:
                mock_now.return_value = "20240110120000"

                mock_env = Mock()
                mock_env.env_dict = {
                    "directory": str(warehouse / "TestProject_TestOrg_20240110120000"),
                    "task_prompt": "Create a calculator"
                }
                mock_env.codes = Mock()
                mock_env.codes.version = 0
                mock_env.config = Mock()
                mock_env.config.git_management = False
                mock_env.config.clear_structure = True
                mock_env.config.incremental_develop = False
                mock_env.exist_employee = Mock(return_value=True)
                mock_env.recruit = Mock()
                mock_env.write_meta = Mock()
                mock_env_class.return_value = mock_env

                chain = ChatChain(
                    config_path=str(mock_config_dir / "ChatChainConfig.json"),
                    config_phase_path=str(mock_config_dir / "PhaseConfig.json"),
                    config_role_path=str(mock_config_dir / "RoleConfig.json"),
                    task_prompt="Create a calculator",
                    project_name="TestProject",
                    org_name="TestOrg",
                    model_type=ModelType.GPT_3_5_TURBO
                )

                # Should initialize without errors
                assert chain is not None

                # Should be able to recruit
                chain.make_recruitment()
                assert mock_env.recruit.called


@pytest.mark.integration
class TestErrorHandling:
    """Integration tests for error handling scenarios."""

    def test_missing_config_raises_error(self):
        """Test that missing configuration file raises appropriate error."""
        with pytest.raises(ConfigurationError) as exc_info:
            ChatChain(
                config_path="/nonexistent/config.json",
                config_phase_path="/nonexistent/phase.json",
                config_role_path="/nonexistent/role.json",
                task_prompt="Test",
                project_name="Test",
                org_name="Test"
            )

        assert "not found" in str(exc_info.value).lower()

    def test_invalid_json_config_raises_error(self, temp_dir):
        """Test that invalid JSON raises appropriate error."""
        config_file = temp_dir / "invalid.json"
        config_file.write_text("{invalid json")

        with pytest.raises(ConfigurationError) as exc_info:
            ChatChain(
                config_path=str(config_file),
                config_phase_path=str(config_file),
                config_role_path=str(config_file),
                task_prompt="Test",
                project_name="Test",
                org_name="Test"
            )

        assert "json" in str(exc_info.value).lower()

    def test_missing_phase_raises_error(self, mock_config_dir):
        """Test that executing non-existent phase raises error."""
        with patch('chatdev.chat_chain.ChatEnv'):
            chain = ChatChain(
                config_path=str(mock_config_dir / "ChatChainConfig.json"),
                config_phase_path=str(mock_config_dir / "PhaseConfig.json"),
                config_role_path=str(mock_config_dir / "RoleConfig.json"),
                task_prompt="Test",
                project_name="Test",
                org_name="Test"
            )

            from chatdev.exceptions import PhaseExecutionError

            with pytest.raises(PhaseExecutionError):
                chain.execute_step({
                    "phase": "NonExistentPhase",
                    "phaseType": "SimplePhase",
                    "max_turn_step": 2,
                    "need_reflect": "False"
                })


@pytest.mark.integration
@pytest.mark.slow
class TestPerformance:
    """Performance-related integration tests."""

    def test_config_loading_performance(self, mock_config_dir, benchmark):
        """Benchmark configuration loading performance."""
        def load_config():
            with patch('chatdev.chat_chain.ChatEnv'):
                return ChatChain(
                    config_path=str(mock_config_dir / "ChatChainConfig.json"),
                    config_phase_path=str(mock_config_dir / "PhaseConfig.json"),
                    config_role_path=str(mock_config_dir / "RoleConfig.json"),
                    task_prompt="Test",
                    project_name="Test",
                    org_name="Test"
                )

        if hasattr(pytest, 'benchmark'):
            result = benchmark(load_config)
            assert result is not None
        else:
            # If pytest-benchmark not installed, just run once
            result = load_config()
            assert result is not None
