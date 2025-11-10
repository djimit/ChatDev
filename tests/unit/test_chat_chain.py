"""
Unit tests for chatdev.chat_chain module.
"""
import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from camel.typing import ModelType
from chatdev.chat_chain import ChatChain, check_bool
from chatdev.exceptions import ConfigurationError, PhaseExecutionError


class TestCheckBool:
    """Test the check_bool utility function."""

    def test_true_lowercase(self):
        """Test 'true' returns True."""
        assert check_bool("true") is True

    def test_true_uppercase(self):
        """Test 'True' returns True."""
        assert check_bool("True") is True

    def test_true_mixed_case(self):
        """Test 'TrUe' returns True."""
        assert check_bool("TrUe") is True

    def test_false(self):
        """Test 'false' returns False."""
        assert check_bool("false") is False

    def test_empty_string(self):
        """Test empty string returns False."""
        assert check_bool("") is False

    def test_other_string(self):
        """Test other strings return False."""
        assert check_bool("yes") is False


class TestChatChainInit:
    """Test ChatChain initialization."""

    def test_missing_config_file(self, mock_config_dir):
        """Test that missing config file raises ConfigurationError."""
        with pytest.raises(ConfigurationError) as exc_info:
            ChatChain(
                config_path="/nonexistent/config.json",
                config_phase_path=str(mock_config_dir / "PhaseConfig.json"),
                config_role_path=str(mock_config_dir / "RoleConfig.json"),
                task_prompt="Test task",
                project_name="TestProject",
                org_name="TestOrg"
            )
        assert "not found" in str(exc_info.value).lower()

    def test_invalid_json_config(self, temp_dir):
        """Test that invalid JSON raises ConfigurationError."""
        config_file = temp_dir / "invalid.json"
        config_file.write_text("{invalid json")

        with pytest.raises(ConfigurationError) as exc_info:
            ChatChain(
                config_path=str(config_file),
                config_phase_path=str(config_file),
                config_role_path=str(config_file),
                task_prompt="Test task",
                project_name="TestProject",
                org_name="TestOrg"
            )
        assert "invalid json" in str(exc_info.value).lower()

    @patch('chatdev.chat_chain.ChatEnv')
    def test_successful_init(self, mock_env, mock_config_dir):
        """Test successful ChatChain initialization."""
        chain = ChatChain(
            config_path=str(mock_config_dir / "ChatChainConfig.json"),
            config_phase_path=str(mock_config_dir / "PhaseConfig.json"),
            config_role_path=str(mock_config_dir / "RoleConfig.json"),
            task_prompt="Create a calculator",
            project_name="Calculator",
            org_name="TestOrg",
            model_type=ModelType.GPT_3_5_TURBO
        )

        assert chain.project_name == "Calculator"
        assert chain.org_name == "TestOrg"
        assert chain.task_prompt_raw == "Create a calculator"
        assert chain.model_type == ModelType.GPT_3_5_TURBO
        assert isinstance(chain.config, dict)
        assert isinstance(chain.config_phase, dict)
        assert isinstance(chain.config_role, dict)

    @patch('chatdev.chat_chain.ChatEnv')
    def test_role_prompts_loaded(self, mock_env, mock_config_dir):
        """Test that role prompts are properly loaded."""
        chain = ChatChain(
            config_path=str(mock_config_dir / "ChatChainConfig.json"),
            config_phase_path=str(mock_config_dir / "PhaseConfig.json"),
            config_role_path=str(mock_config_dir / "RoleConfig.json"),
            task_prompt="Test task",
            project_name="TestProject",
            org_name="TestOrg"
        )

        assert "Chief Executive Officer" in chain.role_prompts
        assert "Chief Product Officer" in chain.role_prompts
        assert chain.role_prompts["Chief Executive Officer"] == "You are a CEO"


class TestChatChainMakeRecruitment:
    """Test ChatChain make_recruitment method."""

    @patch('chatdev.chat_chain.ChatEnv')
    def test_recruits_all_employees(self, mock_env_class, mock_config_dir):
        """Test that all configured employees are recruited."""
        mock_env_instance = Mock()
        mock_env_class.return_value = mock_env_instance

        chain = ChatChain(
            config_path=str(mock_config_dir / "ChatChainConfig.json"),
            config_phase_path=str(mock_config_dir / "PhaseConfig.json"),
            config_role_path=str(mock_config_dir / "RoleConfig.json"),
            task_prompt="Test task",
            project_name="TestProject",
            org_name="TestOrg"
        )

        chain.make_recruitment()

        # Should recruit CEO and CPO as specified in mock config
        assert mock_env_instance.recruit.call_count == 2
        mock_env_instance.recruit.assert_any_call(agent_name="Chief Executive Officer")
        mock_env_instance.recruit.assert_any_call(agent_name="Chief Product Officer")


class TestChatChainExecuteStep:
    """Test ChatChain execute_step method."""

    @patch('chatdev.chat_chain.ChatEnv')
    def test_simple_phase_not_implemented(self, mock_env, mock_config_dir):
        """Test that unimplemented SimplePhase raises PhaseExecutionError."""
        chain = ChatChain(
            config_path=str(mock_config_dir / "ChatChainConfig.json"),
            config_phase_path=str(mock_config_dir / "PhaseConfig.json"),
            config_role_path=str(mock_config_dir / "RoleConfig.json"),
            task_prompt="Test task",
            project_name="TestProject",
            org_name="TestOrg"
        )

        phase_item = {
            "phase": "NonexistentPhase",
            "phaseType": "SimplePhase",
            "max_turn_step": 2,
            "need_reflect": "False"
        }

        with pytest.raises(PhaseExecutionError) as exc_info:
            chain.execute_step(phase_item)

        assert "not yet implemented" in str(exc_info.value).lower()
        assert exc_info.value.phase_name == "NonexistentPhase"
        assert exc_info.value.phase_type == "SimplePhase"

    @patch('chatdev.chat_chain.ChatEnv')
    def test_composed_phase_not_implemented(self, mock_env, mock_config_dir):
        """Test that unimplemented ComposedPhase raises PhaseExecutionError."""
        chain = ChatChain(
            config_path=str(mock_config_dir / "ChatChainConfig.json"),
            config_phase_path=str(mock_config_dir / "PhaseConfig.json"),
            config_role_path=str(mock_config_dir / "RoleConfig.json"),
            task_prompt="Test task",
            project_name="TestProject",
            org_name="TestOrg"
        )

        phase_item = {
            "phase": "NonexistentComposedPhase",
            "phaseType": "ComposedPhase",
            "cycleNum": 3,
            "Composition": []
        }

        with pytest.raises(PhaseExecutionError) as exc_info:
            chain.execute_step(phase_item)

        assert "not yet implemented" in str(exc_info.value).lower()
        assert exc_info.value.phase_name == "NonexistentComposedPhase"

    @patch('chatdev.chat_chain.ChatEnv')
    def test_invalid_phase_type(self, mock_env, mock_config_dir):
        """Test that invalid phaseType raises PhaseExecutionError."""
        chain = ChatChain(
            config_path=str(mock_config_dir / "ChatChainConfig.json"),
            config_phase_path=str(mock_config_dir / "PhaseConfig.json"),
            config_role_path=str(mock_config_dir / "RoleConfig.json"),
            task_prompt="Test task",
            project_name="TestProject",
            org_name="TestOrg"
        )

        phase_item = {
            "phase": "TestPhase",
            "phaseType": "InvalidPhaseType",
            "max_turn_step": 2
        }

        with pytest.raises(PhaseExecutionError) as exc_info:
            chain.execute_step(phase_item)

        assert "not yet implemented" in str(exc_info.value).lower()
        assert exc_info.value.phase_type == "InvalidPhaseType"


class TestChatChainGetConfig:
    """Test the get_config helper function."""

    def test_get_config_with_custom_files(self, temp_dir):
        """Test get_config returns custom config files when they exist."""
        from chatdev.chat_chain import ChatChain
        import chatdev.chat_chain as chat_chain_module

        # Create custom config directory
        custom_dir = temp_dir / "CompanyConfig" / "Custom"
        custom_dir.mkdir(parents=True)

        # Create default config directory
        default_dir = temp_dir / "CompanyConfig" / "Default"
        default_dir.mkdir(parents=True)

        # Create config files
        for directory in [custom_dir, default_dir]:
            for filename in ["ChatChainConfig.json", "PhaseConfig.json", "RoleConfig.json"]:
                (directory / filename).write_text("{}")

        # Temporarily patch the root directory
        original_file = chat_chain_module.__file__
        with patch.object(chat_chain_module, '__file__', str(temp_dir / "chatdev" / "chat_chain.py")):
            # Mock os.path.dirname to return our temp dir
            with patch('os.path.dirname') as mock_dirname:
                mock_dirname.side_effect = lambda x: str(temp_dir) if 'chat_chain.py' in x else str(temp_dir / "chatdev")

                from run import get_config
                config_paths = get_config("Custom")

                # Should return custom config files
                assert str(custom_dir / "ChatChainConfig.json") in config_paths[0]
