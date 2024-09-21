"""
LLM CLI: A Command Line Interface for interacting with Language Models.

This module provides functionality to execute shell commands, interact with
language models, and process user queries through a command-line interface.
"""

import os
import sys
import re
import shlex
import argparse
from subprocess import Popen, PIPE, STDOUT
from termcolor import colored
from halo import Halo
from llm_cli.llm_cli_helper.shell import Shell
from llm_cli.llm_cli_helper.chat import Chat, Role, Message
from llm_cli.llm_cli_helper.prompt import Prompt


def handle_cd_command(command_parts):
    """
    Handle the 'cd' command and change the current working directory.

    Args:
        command_parts (list): List of command parts.

    Returns:
        bool: True if 'cd' command was handled, False otherwise.
    """
    for index, cmd in enumerate(command_parts):
        if cmd == "cd" and index + 1 < len(command_parts):
            new_dir = command_parts[index + 1]
            try:
                os.chdir(new_dir)
                print(colored(f"Changed directory to: {os.getcwd()}", "green"))
            except Exception as e:
                print(colored(f"Failed to change directory to {new_dir}: {e}", "red"))
            return True
    return False


def execute_single_command(shell, command):
    """
    Execute a single shell command directly in the terminal.

    Args:
        shell (Shell): Shell object containing the selected shell.
        command (str): Command to execute.
    """
    process = Popen([shell.selected, "-c", command], stdin=PIPE, stderr=STDOUT)
    process.wait()

    if process.returncode == 0:
        print(colored(f"Command '{command}' executed successfully!", "green"))
    else:
        print(colored(f"Command failed with exit code: {process.returncode}", "red"))


def execute_commands(shell, full_command):
    """
    Split and execute both composite and non-composite commands.

    Args:
        shell (Shell): Shell object containing the selected shell.
        full_command (str): Full command string to execute.
    """
    command_parts = full_command.split("&&") if "&&" in full_command else [full_command]

    for command in command_parts:
        command = command.strip()

        if command.startswith("cd "):
            args = shlex.split(command)
            if handle_cd_command(args):
                continue

        execute_single_command(shell, command)


def main():
    """
    Main function to handle CLI arguments, initialize services, and process user requests.
    """
    parser = argparse.ArgumentParser(description="Command Line Interface for LLM")
    parser.add_argument("-m", "--model", help="specify a LLM model to use", type=str)
    parser.add_argument(
        "-q",
        "--query",
        help="Just ask a question of the LLM and return the response",
        action="store_true",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Output all the request and response data",
        action="store_true",
    )
    parser.add_argument(
        "command", nargs="*", help="The command or query to be processed"
    )

    args = parser.parse_args()
    model = args.model or os.getenv("LLM_MODEL", "")
    is_query = args.query
    verbose = args.verbose

    # Initialize services
    shell = Shell()
    spin = Halo(text="Processing", spinner="dots")

    try:
        chat = Chat.service()
    except Chat.Error as error:
        print(colored(error.message, "red"))
        _print_chat_requirements()
        sys.exit(1)

    chat.model_preference = model
    if verbose:
        print(colored(f"> Model Selected: {chat.model_id()}", "red"))

    if is_query and args.command:
        _handle_query_mode(args, chat, shell, spin)
    else:
        _handle_command_mode(args, chat, shell, spin, verbose)


def _print_chat_requirements():
    """Print the requirements for the Chat service."""
    for req in Chat.requirements():
        print(f"\n{req['name']}")
        print("env vars:\n - " + "\n - ".join(req["requires"]))
        optional = req.get("optional")
        if optional:
            print(" - " + "\n - ".join([f"{opt} (optional)" for opt in optional]))
        print(req["help"])


def _handle_query_mode(args, chat, shell, spin):
    """Handle the query mode of the CLI."""
    question = " ".join(args.command).strip()
    if question:
        messages = [Message(Role.USER, question)]
        while True:
            try:
                message_dicts = [msg.to_dict() for msg in messages]
                spin.start()
                response = chat.chat(message_dicts)
                messages.append(Message.from_dict(response))
                spin.stop()

                print(colored(f"\n{response.content}\n", "green"))

                question = shell.get_input("reply? ").strip()

                if question.lower() == "exit":
                    print("Exiting chat.")
                    sys.exit(0)

                if not question:
                    sys.exit(0)

                messages.append(Message(Role.USER, question))

            except KeyboardInterrupt:
                print("\nProcess interrupted. Exiting gracefully.")
                sys.exit(0)


def _handle_command_mode(args, chat, shell, spin, verbose):
    """Handle the command mode of the CLI."""
    prompt = Prompt(
        [
            "No user assistance, command ordering is important",
            f"You are running on {shell.operating_system()}",
            f"The current shell is: {os.path.basename(shell.selected)}",
            "Wrap unknown command parameters in <brackets>",
            "you might need to change directory before executing subsequent commands",
            "a single command might solve multiple goals, be creative",
        ]
    )

    request = " ".join(args.command).strip()
    if not request:
        print(colored("No command description provided", "red"))
        sys.exit(1)

    prompt.add_goal(request)
    prompt_message = prompt.generate()
    if verbose:
        print(colored(f"> Requesting:\n{prompt_message}\n", "red"))

    try:
        spin.start()
        response = chat.send(prompt_message)
        spin.stop()

        if verbose:
            print(colored(f"> Raw response:\n{response}\n", "red"))

        cmds = prompt.parse_response(response)
        if not cmds:
            print(colored("Failed to generate commands:", "red"))
            print(colored(cmds.speak or cmds.criticism or cmds.text, "red"))
            sys.exit(0)

        _process_commands(cmds, shell)

    except Exception as error:
        spin.stop()
        print(colored(str(error), "red"))
        sys.exit(2)


def _process_commands(cmds, shell):
    """Process and execute the generated commands."""
    print(colored(cmds.speak or cmds.text, "dark_grey"))
    if cmds.criticism:
        print(colored(f"  - NOTE: {cmds.criticism}", "dark_grey"))

    print(colored("Commands:", "dark_grey"))
    for cmd in cmds.commands:
        print(colored(f" > {cmd.command}", "dark_grey"))

    pattern = r"<(?P<content1>[a-zA-Z0-9_\-\ ]+)>|%\{(?P<content2>[^}]+)\}"
    previous = {}

    try:
        for cmd in cmds.commands:
            _execute_command(cmd, shell, pattern, previous)
    except KeyboardInterrupt:
        print("\nProcess interrupted. Exiting gracefully.")
        sys.exit(0)


def _execute_command(cmd, shell, pattern, previous):
    """Execute a single command with user input handling."""
    print(colored(f"\n{cmd.description}", "green"))
    print(colored(f"preparing: {cmd.command}", "dark_grey"))

    current = {}
    for match_data in re.finditer(pattern, cmd.command):
        match = match_data.group("content1") or match_data.group("content2")
        if match in current:
            continue

        if match in previous:
            input_value = (
                shell.get_input(f"{match} [{previous[match]}]: ").strip()
                or previous[match]
            )
        else:
            input_value = shell.get_input(f"{match}: ").strip()

        current[match] = (match_data.group(0), input_value)
        previous[match] = input_value

    execute = cmd.command
    for _, (sub, replacement) in current.items():
        execute = execute.replace(sub, replacement)

    print(colored(execute, "dark_grey"))
    do_exec = shell.get_input(colored("Execute [Y]? ", "green")).strip()

    if do_exec.lower() == "exit":
        print(colored("Exiting process.", "red"))
        sys.exit(0)

    if not do_exec.lower().startswith("y"):
        print(colored("Failed to approve command execution.", "red"))
        sys.exit(0)

    execute_commands(shell, execute)


if __name__ == "__main__":
    main()
