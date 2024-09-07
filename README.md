
# LLM-CLI

[![Poetry](https://img.shields.io/badge/poetry-managed-blue)](https://python-poetry.org/)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/release/python-3110/)

**LLM-CLI** is a command-line interface (CLI) tool designed to interact with large language models (LLMs) and execute shell commands. This tool allows users to send natural language queries to an LLM and receive responses or execute commands interactively.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Basic Command](#basic-command)
  - [Interactive Mode](#interactive-mode)
  - [Options](#options)
- [Configuration](#configuration)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- Query large language models (LLMs) directly from the command line.
- Interactive chat mode for continuous dialogue with the LLM.
- Execute shell commands, including `cd`, and chain commands using `&&`.
- Verbose mode to print raw responses and other debugging information.
- Error handling with detailed feedback for API or shell execution errors.
- Dynamic prompt generation to assist in completing complex shell commands.

## Installation

Since this project is not deployed on PyPI, you can install it locally using `pipx` or `pip` with the built `.whl` file.

### 1. Build the Project

First, build the `.whl` file using Poetry:

```bash
poetry build
```

This will generate a `.whl` file inside the `dist/` directory.

### 2. Install Using `pipx` (Recommended)

To install the package with `pipx`, use the following command:

```bash
pipx install dist/llm_cli-0.1.0-py3-none-any.whl
```

This installs the CLI tool in an isolated environment, making it easy to manage.

### 3. Install Using `pip`

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

This will send the query to the LLM and return a response.

### Interactive Mode

You can enter an interactive mode where the tool continues querying the LLM and waits for further input:

```bash
llm -q "Start an interactive session"
```

In interactive mode, after each response, you can continue the conversation or type `exit` to end the session.

### Options

- `-q, --query`: The query you wish to send to the LLM (required for non-interactive usage).
- `-m, --model`: Specify the LLM model to use. Can be set via environment variables or passed in the command.
- `-v, --verbose`: Output additional information about the request and response.
- `command`: Any shell command or query to execute through the CLI.

### Command Execution

LLM-CLI also supports running shell commands. You can execute both composite (`&&` chained) and non-composite commands:

```bash
llm "cd /some/path && ls -la"
```

The CLI handles the `cd` command internally and provides feedback on success or failure.

## Configuration

LLM-CLI allows you to configure API keys, LLM models, and other settings using a `.llm-cli-config.json` file in your home directory:

```json
{
    "api_key": "your-api-key",
    "model": "your-preferred-llm-model"
}
```

Place this file in your home directory (`~/.llm-cli-config.json`), and the CLI will automatically use these settings.

### Example Configuration

```json
{
    "api_key": "sk-123456789",
    "model": "gpt-3.5"
}
```

## Development

If you wish to contribute or further develop the tool, follow these steps to set up a local development environment:

### Set up Poetry Environment

```bash
git clone https://github.com/your-repo/llm-cli.git
cd llm-cli
poetry install
```

### Running Locally

To run the CLI in development mode:

```bash
poetry run llm -q "Test query"
```

### Tests

You can run the tests using `pytest`:

```bash
pytest
```

## Contributing

Contributions are welcome! Feel free to submit a pull request or open an issue on the [GitHub repository](https://github.com/your-repo/llm-cli/issues).

### Guidelines

1. Fork the repository.
2. Create a new branch for your feature/bugfix.
3. Submit a pull request when you're ready.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
