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
from llm_cli.llm_cli_helper.chat_helper.gpt import GPT
from llm_cli.llm_cli_helper.prompt import Prompt
from llm_cli.llm_cli_helper.prompt_helper.response import PromptResponse, Command, Thoughts

def handle_cd_command(command_parts):
    """Handles the 'cd' part of the command and changes the directory."""
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
    """Executes a single shell command directly in the terminal."""
    process = Popen([shell.selected, "-c", command], stdin=PIPE, stderr=STDOUT)

    # Wait for process to complete and ensure print output goes to terminal
    process.wait()

    # Handle output and check for success
    if process.returncode == 0:
        print(colored(f"Command '{command}' executed successfully!", "green"))
    else:
        print(colored(f"Command failed with exit code: {process.returncode}", "red"))

def execute_commands(shell, full_command):
    """Splits and executes both composite and non-composite commands."""
    command_parts = full_command.split("&&") if '&&' in full_command else [full_command]

    for command in command_parts:
        command = command.strip()

        # Check if it's a 'cd' command and handle directory changes
        if command.startswith("cd "):
            args = shlex.split(command)
            if handle_cd_command(args):
                continue  # Skip executing 'cd' as a shell command
        
        # For non-cd commands, execute them normally
        execute_single_command(shell, command)


def main():
    # Check for any runtime flags
    args = sys.argv[1:]
    verbose = False
    is_query = False
    model = os.getenv("LLM_MODEL", "")

    # Command line options
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
    if args.model:
        model = args.model
    if args.query:
        is_query = True
    if args.verbose:
        verbose = True

    # Initialize the service
    shell = Shell()
    spin = Halo(text="Processing", spinner="dots")
    try:
        chat = Chat.service()
    except Chat.Error as error:
        print(colored(error.message, "red"))
        for req in Chat.requirements():
            print(f"\n{req['name']}")
            print("env vars:\n - " + "\n - ".join(req["requires"]))
            optional = req.get("optional")
            if optional:
                print(" - " + "\n - ".join([f"{opt} (optional)" for opt in optional]))
            print(req["help"])
        sys.exit(1)

    chat.model_preference = model
    if verbose:
        print(colored(f"> Model Selected: {chat.model_id()}", "red"))

    # We want to ask some questions via the command line
    if is_query and args:
        question = " ".join(args.command).strip()
        if question:
            try:
                messages = [Message(Role.User, question, None)]
                message_dicts = [msg.to_dict() for msg in messages]
                while True:
                    try:
                        spin.start()  # Start spinner if implemented
                        response = chat.chat(message_dicts)
                        messages.append(response)
                        spin.stop()  # Stop spinner if implemented

                        print(colored(f"\n{response.content}\n", "green"))

                        question = shell.get_input("reply? ").strip()

                        # Check for 'exit' input
                        if question.lower() == "exit":
                            print("Exiting chat.")
                            sys.exit(0)

                        if not question:
                            sys.exit(0)

                        messages.append(Message(Role.User, question, None))
                        message_dicts = [msg.to_dict() for msg in messages]

                    except KeyboardInterrupt:
                        print("\nProcess interrupted. Exiting gracefully.")
                        sys.exit(0)

            except Exception as error:
                spin.stop()  # Stop spinner if implemented
                print(colored(str(error), "red"))
                sys.exit(2)

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

    # Grab the user's request
    request = " ".join(args.command).strip()
    if not request:
        print(colored("No command description provided", "red"))
        sys.exit(1)

    prompt.add_goal(request)
    prompt_message = prompt.generate()
    if verbose:
        print(colored(f"> Requesting:\n{prompt_message}\n", "red"))

    try:
        spin.start()  # Start spinner if implemented
        response = chat.send(prompt_message)
        spin.stop()  # Stop spinner if implemented

        if verbose:
            print(colored(f"> Raw response:\n{response}\n", "red"))

        try:
            cmds = PromptResponse.from_json(response)
            if not cmds:
                print(colored("Failed to generate commands:", "red"))
                print(colored(cmds.speak or cmds.criticism or cmds.text, "red"))
                sys.exit(0)

            # Provide the user feedback
            print(colored(cmds.speak or cmds.text, "dark_grey"))
            if cmds.criticism:
                print(colored(f"  - NOTE: {cmds.criticism}", "dark_grey"))

            # Execute commands
            pattern = r"<(?P<content1>[a-zA-Z0-9_\-\ ]+)>|%\{(?P<content2>[^}]+)\}"
            previous = {}

            print(colored("Commands:", "dark_grey"))
            for cmd in cmds.commands:
                print(colored(f" > {cmd.command}", "dark_grey"))
            try:
                for cmd in cmds.commands:
                    current = {}

                    print(colored(f"\n{cmd.description}", "green"))
                    print(colored(f"preparing: {cmd.command}", "dark_grey"))

                    for match_data in re.finditer(pattern, cmd.command):
                        match = match_data.group("content1") or match_data.group(
                            "content2"
                        )
                        if match in current:
                            continue

                        if match in previous:
                            input_value = (
                                shell.get_input(
                                    f"{match} [{previous[match]}]: "
                                ).strip()
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
                    do_exec = shell.get_input("execute [Y]? ").strip()

                    # Check for 'exit' command before executing
                    if do_exec.lower() == "exit":
                        print("Exiting process.")
                        sys.exit(0)

                    if not do_exec or do_exec.lower().startswith("y"):
                        execute_commands(shell, execute)
            except KeyboardInterrupt:
                print("\nProcess interrupted. Exiting gracefully.")
                sys.exit(0)
        except Exception as error:
            print(colored(str(error), "red"))
            print(f"response was:\n{colored(response, 'yellow')}")
            sys.exit(3)
    except Exception as error:
        spin.stop()  # Stop spinner if implemented
        print(colored(str(error), "red"))
        sys.exit(2)
