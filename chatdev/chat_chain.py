import importlib
import json
import logging
import os
import shutil
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

from camel.agents import RolePlaying
from camel.configs import ChatGPTConfig
from camel.typing import TaskType, ModelType
from chatdev.chat_env import ChatEnv, ChatEnvConfig
from chatdev.exceptions import (
    ConfigurationError,
    PhaseExecutionError,
    GitOperationError
)
from chatdev.statistics import get_info
from chatdev.utils import log_and_print_online, now


def check_bool(s: str) -> bool:
    """Convert string to boolean value.

    Args:
        s: String to convert (case-insensitive)

    Returns:
        True if string is 'true' (case-insensitive), False otherwise

    Example:
        >>> check_bool("true")
        True
        >>> check_bool("False")
        False
    """
    return s.lower() == "true"


class ChatChain:

    def __init__(self,
                 config_path: str = None,
                 config_phase_path: str = None,
                 config_role_path: str = None,
                 task_prompt: str = None,
                 project_name: str = None,
                 org_name: str = None,
                 model_type: ModelType = ModelType.GPT_3_5_TURBO,
                 code_path: str = None) -> None:
        """

        Args:
            config_path: path to the ChatChainConfig.json
            config_phase_path: path to the PhaseConfig.json
            config_role_path: path to the RoleConfig.json
            task_prompt: the user input prompt for software
            project_name: the user input name for software
            org_name: the organization name of the human user
        """

        # load config file
        self.config_path = config_path
        self.config_phase_path = config_phase_path
        self.config_role_path = config_role_path
        self.project_name = project_name
        self.org_name = org_name
        self.model_type = model_type
        self.code_path = code_path

        try:
            with open(self.config_path, 'r', encoding="utf8") as file:
                self.config = json.load(file)
        except FileNotFoundError:
            raise ConfigurationError(
                f"Configuration file not found: {self.config_path}",
                config_path=self.config_path
            )
        except json.JSONDecodeError as e:
            raise ConfigurationError(
                f"Invalid JSON in configuration file: {e}",
                config_path=self.config_path
            )

        try:
            with open(self.config_phase_path, 'r', encoding="utf8") as file:
                self.config_phase = json.load(file)
        except FileNotFoundError:
            raise ConfigurationError(
                f"Phase configuration file not found: {self.config_phase_path}",
                config_path=self.config_phase_path
            )
        except json.JSONDecodeError as e:
            raise ConfigurationError(
                f"Invalid JSON in phase configuration: {e}",
                config_path=self.config_phase_path
            )

        try:
            with open(self.config_role_path, 'r', encoding="utf8") as file:
                self.config_role = json.load(file)
        except FileNotFoundError:
            raise ConfigurationError(
                f"Role configuration file not found: {self.config_role_path}",
                config_path=self.config_role_path
            )
        except json.JSONDecodeError as e:
            raise ConfigurationError(
                f"Invalid JSON in role configuration: {e}",
                config_path=self.config_role_path
            )

        # init chatchain config and recruitments
        self.chain = self.config["chain"]
        self.recruitments = self.config["recruitments"]

        # init default max chat turn
        self.chat_turn_limit_default = 10

        # init ChatEnv
        self.chat_env_config = ChatEnvConfig(clear_structure=check_bool(self.config["clear_structure"]),
                                             gui_design=check_bool(self.config["gui_design"]),
                                             git_management=check_bool(self.config["git_management"]),
                                             incremental_develop=check_bool(self.config["incremental_develop"]))
        self.chat_env = ChatEnv(self.chat_env_config)

        # the user input prompt will be self-improved (if set "self_improve": "True" in ChatChainConfig.json)
        # the self-improvement is done in self.preprocess
        self.task_prompt_raw = task_prompt
        self.task_prompt = ""

        # init role prompts
        self.role_prompts = dict()
        for role in self.config_role:
            self.role_prompts[role] = "\n".join(self.config_role[role])

        # init log
        self.start_time, self.log_filepath = self.get_logfilepath()

        # init SimplePhase instances
        # import all used phases in PhaseConfig.json from chatdev.phase
        # note that in PhaseConfig.json there only exist SimplePhases
        # ComposedPhases are defined in ChatChainConfig.json and will be imported in self.execute_step
        self.compose_phase_module = importlib.import_module("chatdev.composed_phase")
        self.phase_module = importlib.import_module("chatdev.phase")
        self.phases = dict()
        for phase in self.config_phase:
            assistant_role_name = self.config_phase[phase]['assistant_role_name']
            user_role_name = self.config_phase[phase]['user_role_name']
            phase_prompt = "\n\n".join(self.config_phase[phase]['phase_prompt'])
            phase_class = getattr(self.phase_module, phase)
            phase_instance = phase_class(assistant_role_name=assistant_role_name,
                                         user_role_name=user_role_name,
                                         phase_prompt=phase_prompt,
                                         role_prompts=self.role_prompts,
                                         phase_name=phase,
                                         model_type=self.model_type,
                                         log_filepath=self.log_filepath)
            self.phases[phase] = phase_instance

    def make_recruitment(self) -> None:
        """Recruit all employees for the development team.

        Iterates through the configured recruitment list and adds each
        employee to the chat environment.

        Returns:
            None

        Raises:
            EmployeeNotFoundError: If an employee cannot be recruited
        """
        for employee in self.recruitments:
            self.chat_env.recruit(agent_name=employee)

    def execute_step(self, phase_item: Dict[str, Any]) -> None:
        """Execute a single phase in the development chain.

        Args:
            phase_item: Phase configuration dictionary containing:
                - phase (str): Name of the phase to execute
                - phaseType (str): Type of phase (SimplePhase or ComposedPhase)
                - max_turn_step (int): Maximum conversation turns (SimplePhase only)
                - need_reflect (str): Whether to enable reflection (SimplePhase only)
                - cycleNum (int): Number of cycles (ComposedPhase only)
                - Composition (list): Phase composition (ComposedPhase only)

        Returns:
            None

        Raises:
            PhaseExecutionError: If phase is not implemented or phaseType is invalid
        """

        phase = phase_item['phase']
        phase_type = phase_item['phaseType']
        # For SimplePhase, just look it up from self.phases and conduct the "Phase.execute" method
        if phase_type == "SimplePhase":
            max_turn_step = phase_item['max_turn_step']
            need_reflect = check_bool(phase_item['need_reflect'])
            if phase in self.phases:
                self.chat_env = self.phases[phase].execute(self.chat_env,
                                                           self.chat_turn_limit_default if max_turn_step <= 0 else max_turn_step,
                                                           need_reflect)
            else:
                raise PhaseExecutionError(
                    f"Phase '{phase}' is not yet implemented in chatdev.phase",
                    phase_name=phase,
                    phase_type=phase_type
                )
        # For ComposedPhase, we create instance here then conduct the "ComposedPhase.execute" method
        elif phase_type == "ComposedPhase":
            cycle_num = phase_item['cycleNum']
            composition = phase_item['Composition']
            compose_phase_class = getattr(self.compose_phase_module, phase, None)
            if not compose_phase_class:
                raise PhaseExecutionError(
                    f"Phase '{phase}' is not yet implemented in chatdev.compose_phase",
                    phase_name=phase,
                    phase_type=phase_type
                )
            compose_phase_instance = compose_phase_class(phase_name=phase,
                                                         cycle_num=cycle_num,
                                                         composition=composition,
                                                         config_phase=self.config_phase,
                                                         config_role=self.config_role,
                                                         model_type=self.model_type,
                                                         log_filepath=self.log_filepath)
            self.chat_env = compose_phase_instance.execute(self.chat_env)
        else:
            raise PhaseExecutionError(
                f"PhaseType '{phase_type}' is not yet implemented",
                phase_type=phase_type
            )

    def execute_chain(self) -> None:
        """Execute the entire development chain based on ChatChainConfig.json.

        Iterates through all configured phases and executes them sequentially,
        passing the chat environment between phases.

        Returns:
            None

        Raises:
            PhaseExecutionError: If any phase fails to execute
        """
        for phase_item in self.chain:
            self.execute_step(phase_item)

    def get_logfilepath(self) -> Tuple[str, str]:
        """Get the log file path for this software project.

        Generates a timestamped log file path in the WareHouse directory
        based on project name, organization name, and start time.

        Returns:
            Tuple containing:
                - start_time (str): Timestamp when project started (format: YYYYmmddHHMMSS)
                - log_filepath (str): Full path to the log file

        Example:
            >>> start_time, log_path = self.get_logfilepath()
            >>> print(log_path)
            '/path/to/WareHouse/Calculator_TestOrg_20240110120000.log'
        """
        start_time = now()
        filepath = os.path.dirname(__file__)
        # root = "/".join(filepath.split("/")[:-1])
        root = os.path.dirname(filepath)
        # directory = root + "/WareHouse/"
        directory = os.path.join(root, "WareHouse")
        log_filepath = os.path.join(directory,
                                    "{}.log".format("_".join([self.project_name, self.org_name, start_time])))
        return start_time, log_filepath

    def pre_processing(self) -> None:
        """Perform pre-processing tasks before starting the development chain.

        This includes:
        - Removing temporary files if clear_structure is enabled
        - Creating the software directory
        - Copying configuration files to the project directory
        - Copying existing code for incremental development
        - Logging initialization information
        - Self-improving the task prompt if enabled

        Returns:
            None

        Raises:
            FileOperationError: If file operations fail
            ConfigurationError: If configuration is invalid
        """
        if self.chat_env.config.clear_structure:
            filepath = os.path.dirname(__file__)
            root = os.path.dirname(filepath)
            directory = os.path.join(root, "WareHouse")
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                # logs with error trials are left in WareHouse/
                if os.path.isfile(file_path) and not filename.endswith(".py") and not filename.endswith(".log"):
                    os.remove(file_path)
                    print("{} Removed.".format(file_path))

        software_path = os.path.join(directory, "_".join([self.project_name, self.org_name, self.start_time]))
        self.chat_env.set_directory(software_path)

        # copy config files to software path
        shutil.copy(self.config_path, software_path)
        shutil.copy(self.config_phase_path, software_path)
        shutil.copy(self.config_role_path, software_path)

        # copy code files to software path in incremental_develop mode
        if check_bool(self.config["incremental_develop"]):
            for root, dirs, files in os.walk(self.code_path):
                relative_path = os.path.relpath(root, self.code_path)
                target_dir = os.path.join(software_path, 'base', relative_path)
                os.makedirs(target_dir, exist_ok=True)
                for file in files:
                    source_file = os.path.join(root, file)
                    target_file = os.path.join(target_dir, file)
                    shutil.copy2(source_file, target_file)
            self.chat_env._load_from_hardware(os.path.join(software_path, 'base'))

        # write task prompt to software
        with open(os.path.join(software_path, self.project_name + ".prompt"), "w") as f:
            f.write(self.task_prompt_raw)

        preprocess_msg = "**[Preprocessing]**\n\n"
        chat_gpt_config = ChatGPTConfig()

        preprocess_msg += "**ChatDev Starts** ({})\n\n".format(self.start_time)
        preprocess_msg += "**Timestamp**: {}\n\n".format(self.start_time)
        preprocess_msg += "**config_path**: {}\n\n".format(self.config_path)
        preprocess_msg += "**config_phase_path**: {}\n\n".format(self.config_phase_path)
        preprocess_msg += "**config_role_path**: {}\n\n".format(self.config_role_path)
        preprocess_msg += "**task_prompt**: {}\n\n".format(self.task_prompt_raw)
        preprocess_msg += "**project_name**: {}\n\n".format(self.project_name)
        preprocess_msg += "**Log File**: {}\n\n".format(self.log_filepath)
        preprocess_msg += "**ChatDevConfig**:\n{}\n\n".format(self.chat_env.config.__str__())
        preprocess_msg += "**ChatGPTConfig**:\n{}\n\n".format(chat_gpt_config)
        log_and_print_online(preprocess_msg)

        # init task prompt
        if check_bool(self.config['self_improve']):
            self.chat_env.env_dict['task_prompt'] = self.self_task_improve(self.task_prompt_raw)
        else:
            self.chat_env.env_dict['task_prompt'] = self.task_prompt_raw

    def post_processing(self) -> None:
        """Perform post-processing tasks after development chain completion.

        This includes:
        - Writing metadata for the generated software
        - Performing git operations if git_management is enabled
        - Logging software information and duration
        - Cleaning up temporary files (__pycache__)
        - Moving log files to the software directory

        Returns:
            None

        Raises:
            GitOperationError: If git operations fail
            FileOperationError: If file operations fail
        """

        self.chat_env.write_meta()
        filepath = os.path.dirname(__file__)
        root = os.path.dirname(filepath)

        if self.chat_env_config.git_management:
            git_online_log = "**[Git Information]**\n\n"

            self.chat_env.codes.version += 1
            directory = self.chat_env.env_dict["directory"]

            # Use subprocess.run with proper argument list to prevent command injection
            try:
                subprocess.run(
                    ["git", "add", "."],
                    cwd=directory,
                    check=True,
                    capture_output=True,
                    text=True
                )
                git_online_log += f"git add . (in {directory})\n"
            except subprocess.CalledProcessError as e:
                error_msg = f"Failed to stage files with git add"
                git_online_log += f"Error in git add: {e.stderr}\n"
                raise GitOperationError(
                    error_msg,
                    command="git add .",
                    stderr=e.stderr,
                    return_code=e.returncode
                )

            try:
                commit_message = f"v{self.chat_env.codes.version} Final Version"
                subprocess.run(
                    ["git", "commit", "-m", commit_message],
                    cwd=directory,
                    check=True,
                    capture_output=True,
                    text=True
                )
                git_online_log += f"git commit -m \"{commit_message}\" (in {directory})\n"
            except subprocess.CalledProcessError as e:
                # Allow empty commits to not be an error
                if "nothing to commit" not in e.stderr:
                    error_msg = f"Failed to commit changes"
                    git_online_log += f"Error in git commit: {e.stderr}\n"
                    raise GitOperationError(
                        error_msg,
                        command=f"git commit -m \"{commit_message}\"",
                        stderr=e.stderr,
                        return_code=e.returncode
                    )
                git_online_log += f"Nothing to commit (working tree clean)\n"

            log_and_print_online(git_online_log)

            git_info = "**[Git Log]**\n\n"

            # Execute git log safely
            try:
                completed_process = subprocess.run(
                    ["git", "log"],
                    cwd=directory,
                    text=True,
                    capture_output=True,
                    check=True
                )
                log_output = completed_process.stdout
            except subprocess.CalledProcessError as e:
                log_output = f"Error when executing git log: {e.stderr}"

            git_info += log_output
            log_and_print_online(git_info)

        post_info = "**[Post Info]**\n\n"
        now_time = now()
        time_format = "%Y%m%d%H%M%S"
        datetime1 = datetime.strptime(self.start_time, time_format)
        datetime2 = datetime.strptime(now_time, time_format)
        duration = (datetime2 - datetime1).total_seconds()

        post_info += "Software Info: {}".format(
            get_info(self.chat_env.env_dict['directory'], self.log_filepath) + "\n\n🕑**duration**={:.2f}s\n\n".format(
                duration))

        post_info += "ChatDev Starts ({})".format(self.start_time) + "\n\n"
        post_info += "ChatDev Ends ({})".format(now_time) + "\n\n"

        if self.chat_env.config.clear_structure:
            directory = self.chat_env.env_dict['directory']
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.isdir(file_path) and file_path.endswith("__pycache__"):
                    shutil.rmtree(file_path, ignore_errors=True)
                    post_info += "{} Removed.".format(file_path) + "\n\n"

        log_and_print_online(post_info)

        logging.shutdown()
        time.sleep(1)

        shutil.move(self.log_filepath,
                    os.path.join(root + "/WareHouse", "_".join([self.project_name, self.org_name, self.start_time]),
                                 os.path.basename(self.log_filepath)))

    def self_task_improve(self, task_prompt: str) -> str:
        """Use an AI agent to improve and refine the user's task prompt.

        Engages a Prompt Engineer agent to rewrite the user's task description
        into a more detailed and specific prompt that helps ensure the LLM
        generates correct, runnable software.

        Args:
            task_prompt: Original user query prompt describing the software to build

        Returns:
            Revised and improved task prompt (max 200 words)

        Raises:
            APIError: If the API call to improve the prompt fails

        Example:
            >>> original = "Create a calculator"
            >>> improved = self.self_task_improve(original)
            >>> print(improved)
            "Create a desktop calculator application with basic arithmetic..."
        """
        self_task_improve_prompt = """I will give you a short description of a software design requirement, 
please rewrite it into a detailed prompt that can make large language model know how to make this software better based this prompt,
the prompt should ensure LLMs build a software that can be run correctly, which is the most import part you need to consider.
remember that the revised prompt should not contain more than 200 words, 
here is the short description:\"{}\". 
If the revised prompt is revised_version_of_the_description, 
then you should return a message in a format like \"<INFO> revised_version_of_the_description\", do not return messages in other formats.""".format(
            task_prompt)
        role_play_session = RolePlaying(
            assistant_role_name="Prompt Engineer",
            assistant_role_prompt="You are an professional prompt engineer that can improve user input prompt to make LLM better understand these prompts.",
            user_role_prompt="You are an user that want to use LLM to build software.",
            user_role_name="User",
            task_type=TaskType.CHATDEV,
            task_prompt="Do prompt engineering on user query",
            with_task_specify=False,
            model_type=self.model_type,
        )

        # log_and_print_online("System", role_play_session.assistant_sys_msg)
        # log_and_print_online("System", role_play_session.user_sys_msg)

        _, input_user_msg = role_play_session.init_chat(None, None, self_task_improve_prompt)
        assistant_response, user_response = role_play_session.step(input_user_msg, True)
        revised_task_prompt = assistant_response.msg.content.split("<INFO>")[-1].lower().strip()
        log_and_print_online(role_play_session.assistant_agent.role_name, assistant_response.msg.content)
        log_and_print_online(
            "**[Task Prompt Self Improvement]**\n**Original Task Prompt**: {}\n**Improved Task Prompt**: {}".format(
                task_prompt, revised_task_prompt))
        return revised_task_prompt
