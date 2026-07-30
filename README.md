# Python AI Coding Agent

A command-line AI coding agent built in Python using the OpenAI SDK and any compatible chat-completions API.

The agent can inspect a Python project, search and read its files, modify code, execute Python programs, run development commands, and iteratively use tool results until it completes and verifies a coding task.

This project began as part of the Boot.dev AI Agent course and has since been extended into a more reusable Python coding agent.

## What the Agent Can Do

The agent can:

* Work on a user-selected Python project directory
* List files and directories
* Search text across project files
* Read file contents
* Create or overwrite files
* Execute individual Python files
* Run approved development commands
* Pass optional command-line arguments to Python files
* Run test suites, linters, and type checkers
* Capture standard output, standard error, and process exit codes
* Maintain conversation history between model calls
* Iterate through multiple tool calls
* Stop after completing and verifying the requested task
* Display model, token, tool, and execution details in verbose mode

## Key Improvements

The project has been extended beyond its original calculator-specific implementation.

### Configurable working directory

The agent is no longer restricted to the included calculator project.

Use `--working-directory` to choose the Python project the agent may inspect and modify:

```bash
uv run main.py \
  --working-directory ./calculator \
  "Explain how this project works."
```

You can point it at another local Python project:

```bash
uv run main.py \
  --working-directory ../my-python-project \
  "Run the tests and fix the failing test."
```

The selected directory becomes the permitted workspace for all file and command tools.

### Extracted `Agent` class

The model loop has been moved into an `Agent` class.

The class is responsible for:

* Calling the configured model
* Maintaining conversation history
* Executing requested tools
* Returning tool results to the model
* Tracking token usage in verbose mode
* Enforcing the maximum iteration count
* Returning the final response

This keeps command-line setup separate from the agent's reasoning and execution loop.

### Configurable model provider

The API key, model, base URL, and maximum iteration count can be configured using environment variables or command-line arguments.

This allows the agent to work with OpenRouter and other OpenAI-compatible APIs.

### Project-wide file search

The `search_files` tool searches project text files for:

* Function names
* Class names
* Imports
* Configuration values
* Error messages
* Test names
* Other code references

Search results include the relative file path, line number, and matching line.

The tool skips common generated or dependency directories, including:

* `.git`
* `.venv`
* `venv`
* `__pycache__`
* `.pytest_cache`
* `.mypy_cache`
* `.ruff_cache`
* `node_modules`

### Controlled command execution

The `run_command` tool can run approved Python development commands inside the selected working directory.

Approved commands currently include:

* `python`
* `python3`
* `uv`
* `pytest`
* `ruff`
* `mypy`

Commands are executed without a shell and with a configurable timeout.

Examples include:

```text
["uv", "run", "pytest"]
```

```text
["ruff", "check", "."]
```

```text
["mypy", "."]
```

Unapproved commands are rejected.

## How It Works

The application uses an agent loop:

1. The user provides a coding task.
2. The CLI builds a conversation containing the system prompt and user request.
3. The request is sent to the configured language model with descriptions of the available tools.
4. The model either returns a final answer or requests one or more tool calls.
5. The Python application validates the requested tool name and arguments.
6. The selected tool runs inside the permitted working directory.
7. The tool result is appended to the conversation.
8. The updated conversation is sent back to the model.
9. The process continues until the model returns a final response or reaches the configured iteration limit.

The language model does not directly execute Python functions or shell commands. It requests structured tool calls, while the Python application remains responsible for validation and execution.

## Available Tools

### `get_files_info`

Lists files and directories relative to the selected working directory.

For every item, it returns:

* Name
* File size
* Whether the item is a directory

Example request:

```text
List the files in the src directory.
```

### `get_file_content`

Reads a file relative to the selected working directory.

To avoid sending excessively large files to the model, file content is limited to a configured maximum number of characters. Larger files are truncated with a notice.

Example request:

```text
Read pyproject.toml and explain the project dependencies.
```

### `search_files`

Searches text files for a case-insensitive text query.

Results contain:

* Relative file path
* Line number
* Matching line

Example request:

```text
Find every file that imports OpenAI.
```

### `write_file`

Creates or overwrites a file relative to the selected working directory.

Missing parent directories are created automatically.

Example request:

```text
Create a new tests/test_config.py file with tests for the settings loader.
```

This tool replaces the complete contents of the target file. It should therefore be used carefully.

### `run_python_file`

Executes one Python file relative to the selected working directory.

The tool:

* Accepts optional command-line arguments
* Captures standard output
* Captures standard error
* Reports non-zero exit codes
* Uses a 30-second timeout

Example request:

```text
Run main.py with the argument "3 + 7 * 2".
```

### `run_command`

Runs an approved development command inside the selected working directory.

The tool:

* Accepts the command as a list of strings
* Uses `shell=False`
* Restricts executable names
* Captures standard output and standard error
* Reports non-zero exit codes
* Uses a default timeout of 30 seconds
* Rejects timeouts greater than 120 seconds

Example request:

```text
Run the project tests and explain any failures.
```

## Project Structure

```text
ai-agent/
├── calculator/
│   ├── main.py
│   ├── tests.py
│   └── pkg/
│       ├── calculator.py
│       └── render.py
├── functions/
│   ├── __init__.py
│   ├── get_file_content.py
│   ├── get_files_info.py
│   ├── run_command.py
│   ├── run_python_file.py
│   ├── search_files.py
│   └── write_file.py
├── .env.example
├── .gitignore
├── agent.py
├── call_function.py
├── config.py
├── main.py
├── prompts.py
├── settings.py
├── pyproject.toml
├── test_get_file_content.py
├── test_get_files_info.py
├── test_run_command.py
├── test_run_python_file.py
├── test_search_files.py
├── test_write_file.py
├── uv.lock
└── README.md
```

## Requirements

* Python 3.14 or later
* `uv`
* Access to an OpenAI-compatible chat-completions API
* An API key for the selected provider

## Installation

Clone the repository:

```bash
git clone https://github.com/cyberbotsaber/ai-agent.git
cd ai-agent
```

Install the dependencies:

```bash
uv sync
```

Create your local environment file:

```bash
cp .env.example .env
```

Open `.env` and add your settings:

```env
AI_AGENT_API_KEY=your_api_key_here
AI_AGENT_BASE_URL=https://openrouter.ai/api/v1
AI_AGENT_MODEL=openrouter/free
AI_AGENT_MAX_ITERATIONS=20
```

The older OpenRouter-specific variable is also supported:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

Never commit the `.env` file.

## Configuration

Configuration values may be provided through environment variables or CLI arguments.

### Environment variables

| Variable                  | Purpose                            | Default                        |
| ------------------------- | ---------------------------------- | ------------------------------ |
| `AI_AGENT_API_KEY`        | API key used by the model provider | Required                       |
| `OPENROUTER_API_KEY`      | Fallback OpenRouter API key        | None                           |
| `AI_AGENT_BASE_URL`       | OpenAI-compatible API URL          | `https://openrouter.ai/api/v1` |
| `AI_AGENT_MODEL`          | Model ID                           | `openrouter/free`              |
| `AI_AGENT_MAX_ITERATIONS` | Maximum agent-loop iterations      | `20`                           |

`AI_AGENT_API_KEY` takes priority over `OPENROUTER_API_KEY`.

### Command-line options

Run:

```bash
uv run main.py --help
```

Available options include:

```text
--working-directory
--model
--base-url
--max-iterations
--verbose
```

Command-line values override the related environment-variable settings.

## Usage

### Inspect a project

```bash
uv run main.py \
  --working-directory ./calculator \
  "Explain the structure of this project."
```

### Find code references

```bash
uv run main.py \
  --working-directory ./calculator \
  "Find every file that uses format_json_output."
```

### Run tests

```bash
uv run main.py \
  --working-directory ./calculator \
  "Run the tests and summarize the result."
```

### Fix a bug

```bash
uv run main.py \
  --working-directory ./calculator \
  "Fix the bug: 3 + 7 * 2 shouldn't return 20." \
  --verbose
```

### Use another model

```bash
uv run main.py \
  --working-directory ./calculator \
  --model openrouter/free \
  "Explain how operator precedence is implemented."
```

### Override the API base URL

```bash
uv run main.py \
  --working-directory ./calculator \
  --base-url https://openrouter.ai/api/v1 \
  "List the project files."
```

### Change the iteration limit

```bash
uv run main.py \
  --working-directory ./calculator \
  --max-iterations 10 \
  "Run the tests and fix any failures."
```

### Enable verbose output

```bash
uv run main.py \
  --working-directory ./calculator \
  "Explain what main.py does." \
  --verbose
```

Verbose mode displays:

* User prompt
* Absolute working-directory path
* Model ID
* API base URL
* Maximum iteration count
* Prompt-token usage
* Response-token usage
* Tool names and arguments
* Tool execution results

The API key is never printed.

## Example Agent Workflow

Given this request:

```text
Fix the bug: 3 + 7 * 2 shouldn't return 20.
```

The agent may:

1. List the project files.
2. Search for calculator or precedence-related code.
3. Read the relevant implementation and tests.
4. Run the failing expression.
5. Identify the incorrect precedence value.
6. Update the implementation.
7. Run the calculator test suite.
8. Run the original failing expression again.
9. Return a concise explanation of the change and verification.

## Manual Tests

Run the calculator test suite:

```bash
uv run calculator/tests.py
```

Run the individual tool test modules:

```bash
uv run test_get_files_info.py
uv run test_get_file_content.py
uv run test_write_file.py
uv run test_run_python_file.py
uv run test_search_files.py
uv run test_run_command.py
```

## Security Warning

This project is an educational coding agent, not a production-ready sandbox.

The agent can read, modify, and execute code inside the selected working directory. Its current safeguards include:

* User-selected permitted working directory
* Relative-path validation
* Prevention of ordinary path traversal
* Real-path validation in newer tools
* Restricted command allowlist
* `shell=False` command execution
* Subprocess timeouts
* Maximum agent-loop iterations
* API keys loaded from environment variables
* Ignoring common dependency and generated directories during search

These controls reduce risk but do not create complete process isolation.

Do not:

* Expose this agent as a public service
* Run it against sensitive directories
* Allow untrusted users to supply prompts
* Run it with elevated operating-system privileges
* Assume the working-directory restriction is equivalent to a container or virtual machine

For stronger isolation, run the agent inside a disposable container or virtual machine.

## Limitations

* `write_file` replaces the complete contents of a file.
* The agent does not yet support patch-based editing.
* Tool arguments generated by a model may contain malformed JSON.
* Model behavior varies across providers and models.
* Free model tiers may have strict rate limits.
* The agent may occasionally perform unnecessary tool calls.
* The command allowlist may not include every tool used by a Python project.
* The current path validation is not a full operating-system sandbox.
* Tests are currently run through standalone test scripts rather than a unified automated test suite.
* The project currently focuses on Python repositories.

## Roadmap

Potential future improvements include:

* Patch-based or exact-replacement file editing
* A read-only mode
* User approval before writes or command execution
* Structured logging
* Unified `pytest` coverage for all agent tools
* Mocked model responses for agent-loop tests
* Better API retry and rate-limit handling
* Token and cost budgets
* Detection of repeated tool calls
* Configurable command allowlists
* Project discovery for `pyproject.toml`, `pytest.ini`, `tox.ini`, and other files
* Docker or operating-system-level sandboxing
* Packaging the project as an installable CLI
* Support for additional programming languages

## Development Workflow

Create a feature branch:

```bash
git switch -c feature/my-change
```

Make and test your changes.

Review them:

```bash
git status
git diff
```

Commit:

```bash
git add .
git commit -m "Describe the change"
```

Push:

```bash
git push -u origin feature/my-change
```

Then open a pull request against `main`.

## Educational Purpose

This repository demonstrates:

* OpenAI-compatible tool declarations
* JSON-schema function parameters
* Structured tool dispatch
* Agent conversation loops
* Tool-result feedback
* Filesystem boundary checks
* Controlled subprocess execution
* Runtime configuration
* Prompt design for coding agents

It is intended for learning and experimentation.

## License

This project is currently provided for educational purposes.

Add a licence file before redistributing or using it as the basis of a public production project.

## Author

Created by [cyberbotsaber](https://github.com/cyberbotsaber).
