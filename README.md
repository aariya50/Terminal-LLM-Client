# LLM-CLI

[![Poetry](https://img.shields.io/badge/poetry-managed-blue)](https://python-poetry.org/)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/release/python-3110/)

**LLM-CLI** is a command-line interface (CLI) tool designed to interact with large language models (LLMs) and execute shell commands. This tool allows users to send natural language queries to an LLM and receive responses or execute commands interactively.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Basic Command](#basic-command)
  - [Command Execution](#command-execution)
  - [Options](#options)
- [Configuration](#configuration)
- [Development](#development)
- [License](#license)

## Features

- Query large language models (LLMs) directly from the command line.
- Interactive chat mode for continuous dialogue with the LLM.
- Execute shell commands, including `cd`, and chain commands using `&&`.
- Verbose mode to print raw responses and other debugging information.
- Error handling with detailed feedback for API or shell execution errors.
- Dynamic prompt generation to assist in completing complex shell commands.

## Installation

Since this project is not deployed on PyPI, you can install it locally using `pipx` or `pip` with the built `.whl` file.

### 1. Clone the Repository

First, clone the repository and navigate to the project directory:

```bash
git clone https://github.com/your-repo/llm-cli.git
cd llm-cli
```

### 2. Build the Project

Build the `.whl` file using Poetry:

```bash
poetry build
```

This will generate a `.whl` file inside the `dist/` directory.

### 3. Install Using `pipx` (Recommended)

To install the package with `pipx`, use the following command:

```bash
pipx install dist/llm_cli-0.1.0-py3-none-any.whl
```

This installs the CLI tool in an isolated environment, making it easy to manage.

### 4. Install Using `pip`

Alternatively, you can install the tool using `pip`:

```bash
pip install --user dist/llm_cli-0.1.0-py3-none-any.whl
```

This installs the package for the current user without needing administrator permissions.

## Usage

### Basic Command

To query the LLM, simply run:

```bash
llm -q "Your question here"
```

This will send the query to the LLM and return a response as well as entering an interactive mode where the tool waits for further input. In interactive mode, after each response, you can continue the conversation or type `exit` to end the session.

### Command Execution

LLM-CLI can execute complex shell commands based on natural language requests. The tool breaks down the tasks into multiple steps and asks for confirmation before executing each one.

#### Example

If you request the following task:

```bash
llm "create a dir called test and create a shell script that prints hello world and run it"
```

The tool will break the request into commands and execute them step by step, asking for confirmation before each action.

### Options

- `-q, --query`: The query you wish to send to the LLM (required for non-interactive usage).
- `-m, --model`: Specify the LLM model to use. Can be set via environment variables or passed in the command.
- `-v, --verbose`: Output additional information about the request and response.
- `command`: Any shell command or query to execute through the CLI.

## Configuration

LLM-CLI uses the `OPENAI_API_KEY` environment variable for API access.

### Set the API Key

In your terminal, set the `OPENAI_API_KEY`:

```bash
export OPENAI_API_KEY="your-openai-api-key"
```

LLM-CLI will check if the API key is set before sending any queries.

### Model Selection

If you do not specify a model with the `--model` option, LLM-CLI will automatically default to the model `"gpt-4o-mini"`. The CLI will check the following models in order of preference:

1. The model provided via the `--model` option.
2. Default model: `"gpt-4o-mini"`

## Development

To set up a local development environment:

```bash
git clone https://github.com/your-repo/llm-cli.git
cd llm-cli
poetry install
```

To run the CLI in development mode:

```bash
poetry run llm -q Test query
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is currently unlicensed. Please check back for updates on licensing information.
