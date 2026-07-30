# Python AI Coding Agent

A command-line AI coding agent built in Python using the OpenAI SDK and OpenAI-compatible chat-completions APIs.

The agent can inspect an existing Python project, understand its structure, search and read source code, create new files, modify existing files, execute Python programs, run development commands, and iteratively verify its work.

This project began as part of the Boot.dev AI Agent course and has since been extended into a reusable Python coding agent.

## What the Agent Can Do

The agent can:

* Work on a user-selected Python project directory
* Inspect project files and directories
* Search source code by text
* Read file contents
* Create new Python modules, tests, configuration files, and documentation
* Create missing parent directories when writing new files
* Replace the contents of existing files
* Execute individual Python files
* Run approved development commands
* Run test suites, linters, and type checkers
* Pass command-line arguments to Python programs
* Capture standard output, standard error, and exit codes
* Maintain conversation history across tool calls
* Diagnose bugs and implement fixes
* Build small features from a natural-language request
* Verify new or modified code before reporting completion
* Display detailed model and tool activity in verbose mode

## Can It Create New Code?

Yes.

The agent can use its `write_file` tool to create files that do not already exist. It can also create missing parent directories automatically.

For example, the agent can respond to requests such as:

```text
Create a new validation module for email addresses and add tests for it.
```

```text
Add a tests/test_settings.py file that tests the settings loader.
```

```text
Create a new package called utils with a date-formatting helper.
```

A typical code-generation workflow is:

1. Inspect the project structure.
2. Search for related classes, functions, tests, and conventions.
3. Read the smallest set of relevant files.
4. Decide where the new code belongs.
5. Create the new module or test file.
6. Update related files when necessary.
7. Run the appropriate tests, linter, or type checker.
8. Correct any failures.
9. Return a summary of what was created and how it was verified.

The current file-writing tool writes the complete contents of a file. It does not yet support patch-based editing, so generated changes should be reviewed before merging.

## Key Improvements

The project has been extended beyond its original calculator-specific implementation.

### Configurable working directory

The agent is no longer restricted to the included calculator project.

Use `--working-directory` to select the Python project that the agent may inspect, modify, and execute:

```bash
uv run main.py \
  --working-directory ./calculator \
  "Explain how this project works."
```

You can point it at another local Python project:

```bash
uv run main.py \
  --working-directory ../my-python-project \
  "Create tests for the settings module."
```

The selected directory becomes the permitted workspace for every file and command tool.

### Extracted `Agent` class

The model loop is implemented in a dedicated `Agent` class.

The class is responsible for:

* Calling the configured model
* Maintaining conversation history
* Handling requested tool calls
* Returning tool results to the model
* Tracking token usage in verbose mode
* Enforcing the maximum iteration count
* Returning the final response

This keeps command-line setup separate from agent execution.

### Configurable model provider

The API key, model, API base URL, and maximum iteration count can be configured through environment variables or command-line arguments.

This allows the project to use OpenRouter or another OpenAI-compatible API.

### Project-wide file search

The `search_files` tool searches project text files for:

* Function names
* Class names
* Imports
* Configuration values
* Error messages
* Test names
* Other code references

Results include the relative file path, line number, and matching line.

The search skips common generated and dependency directories:

* `.git`
* `.venv`
* `venv`
* `__pycache__`
* `.pytest_cache`
* `.mypy_cache`
* `.ruff_cache`
* `node_modules`

### Controlled command execution

The `run_command` tool runs approved Python development commands inside the selected working directory.

Approved commands currently include:

* `python`
* `python3`
* `uv`
* `pytest`
* `ruff`
* `mypy`

Commands are passed as a list of strings and run with `shell=False`.

Examples:

```text
["uv", "run", "pytest"]
```

```text
["ruff", "check", "."]
```

```text
["mypy", "."]
```

Commands outside the allowlist are rejected.

## How It Works

The application uses an agent loop:

1. The user provides a coding task.
2. The CLI creates a conversation containing the system prompt and user request.
3. The conversation is sent to the configured language model with descriptions of the available tools.
4. The model either returns a final answer or requests one or more tool calls.
5. The Python application validates the requested tool and its arguments.
6. The selected tool runs inside the permitted working directory.
7. The tool result is appended to the conversation.
8. The updated conversation is sent back to the model.
9. The process continues until the task is complete or the maximum iteration count is reached.

The model does not execute files or functions directly. It requests structured tool calls, while the Python application performs the validation and execution.

## Available Tools

### `get_files_info`

Lists files and directories relative to the selected working directory.

For each item, it returns:

* Name
* File size
* Whether it is a directory

Example request:

```text
List the files in the src directory.
```

### `get_file_content`

Reads a file relative to the selected working directory.

To reduce excessive token usage, the returned content is limited to a configured maximum number of characters. Larger files are truncated with a notice.

Example request:

```text
Read pyproject.toml and explain the dependencies.
```

### `search_files`

Searches text files for a case-insensitive query.

Each result contains:

* Relative file path
* Line number
* Matching line

Example request:

```text
Find every file that imports OpenAI.
```

### `write_file`

Creates a new file or overwrites an existing file relative to the selected working directory.

It can:

* Create a new source-code file
* Create a new test file
* Create a configuration file
* Create documentation
* Create missing parent directories
* Replace an existing file’s complete contents

Example request:

```text
Create tests/test_config.py with unit tests for the settings loader.
```

Important: this tool writes the complete file. It does not yet apply partial patches.

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

* Accepts commands as a list of strings
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

Create the local environment file:

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

Never commit `.env`.

## Configuration

Configuration may be supplied through environment variables or command-line arguments.

### Environment variables

| Variable                  | Purpose                        | Default                        |
| ------------------------- | ------------------------------ | ------------------------------ |
| `AI_AGENT_API_KEY`        | API key for the model provider | Required                       |
| `OPENROUTER_API_KEY`      | Fallback OpenRouter API key    | None                           |
| `AI_AGENT_BASE_URL`       | OpenAI-compatible API URL      | `https://openrouter.ai/api/v1` |
| `AI_AGENT_MODEL`          | Model ID                       | `openrouter/free`              |
| `AI_AGENT_MAX_ITERATIONS` | Maximum agent-loop iterations  | `20`                           |

`AI_AGENT_API_KEY` takes priority over `OPENROUTER_API_KEY`.

### Command-line options

Display the command-line help:

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

Command-line values override the corresponding environment-variable values.

## Usage

### Inspect a Python project

```bash
uv run main.py \
  --working-directory ./calculator \
  "Explain the structure of this project."
```

### Search for code

```bash
uv run main.py \
  --working-directory ./calculator \
  "Find every file that uses format_json_output."
```

### Create a new Python module

```bash
uv run main.py \
  --working-directory ../my-python-project \
  "Create src/utils/validators.py with an email-validation function."
```

### Create tests for existing code

```bash
uv run main.py \
  --working-directory ../my-python-project \
  "Create tests for the settings loader and run them."
```

### Build a small feature

```bash
uv run main.py \
  --working-directory ../my-python-project \
  "Add a JSON export function for customer records and create tests for it."
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
  "Fix the bug: 3 + 7 * 2 should not return 20." \
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
* Tool results

The API key is never printed.

## Example: Creating New Code

Suppose a project does not yet contain a validation module.

Run:

```bash
uv run main.py \
  --working-directory ../my-python-project \
  "Create an email validation module, add unit tests, and run the tests."
```

The agent may:

1. List the project files.
2. Search for existing validation conventions.
3. Read the package structure and current tests.
4. Create a new validation module.
5. Create a new test module.
6. Run the relevant tests.
7. Correct any failures.
8. Return a summary of the new files and verification results.

Always review generated code with:

```bash
git status
git diff
```

## Example: Fixing Existing Code

Given:

```text
Fix the bug: 3 + 7 * 2 should not return 20.
```

The agent may:

1. Inspect the project structure.
2. Search for calculator and precedence-related code.
3. Read the relevant implementation and tests.
4. Reproduce the bug.
5. Identify the incorrect precedence value.
6. Update the implementation.
7. Run the calculator test suite.
8. Run the original failing expression.
9. Return a concise explanation of the fix.

## Manual Tests

Run the calculator test suite:

```bash
uv run calculator/tests.py
```

Run the tool test modules:

```bash
uv run test_get_files_info.py
uv run test_get_file_content.py
uv run test_write_file.py
uv run test_run_python_file.py
uv run test_search_files.py
uv run test_run_command.py
```

## Reviewing Agent-Generated Code

Because the agent can create and overwrite files, always review its work before committing.

Check the repository state:

```bash
git status
```

Review changes:

```bash
git diff
```

Run tests manually:

```bash
uv run pytest
```

Stage only the intended files:

```bash
git add path/to/file.py path/to/test_file.py
```

Commit after verification:

```bash
git commit -m "Add validated feature"
```

## Security Warning

This project is an educational coding agent, not a production-ready sandbox.

The agent can create, read, modify, and execute code inside the selected working directory.

Current safeguards include:

* User-selected permitted working directory
* Relative-path validation
* Prevention of ordinary path traversal
* Real-path validation in newer tools
* Restricted command allowlist
* `shell=False` command execution
* Subprocess timeouts
* Maximum agent-loop iterations
* API keys loaded from environment variables
* Ignoring common generated and dependency directories during search

These controls reduce risk but do not provide complete process isolation.

Do not:

* Expose this agent as a public service
* Run it against sensitive directories
* Allow untrusted users to provide prompts
* Run it with elevated operating-system privileges
* Assume the working-directory restriction is equivalent to a container
* Commit generated changes without reviewing them

For stronger isolation, run the agent inside a disposable container or virtual machine.

## Limitations

* `write_file` replaces a file’s complete contents.
* The agent does not yet support patch-based editing.
* The agent may overwrite valid code if the model generates an incomplete file.
* Tool arguments generated by a model may contain malformed JSON.
* Model behavior varies across providers and models.
* Free model tiers may have strict rate limits.
* The agent may occasionally perform unnecessary tool calls.
* The command allowlist may not include every tool used by a Python project.
* The path checks are not a complete operating-system sandbox.
* The current tests use standalone scripts rather than one unified automated suite.
* The project currently focuses on Python repositories.

## Roadmap

Potential improvements include:

* Patch-based file editing
* Exact text-replacement editing
* Read-only mode
* User approval before file writes
* User approval before command execution
* Automatic backups before overwriting files
* Structured logging
* Unified `pytest` coverage for agent tools
* Mocked model responses for agent-loop tests
* Better API retry and rate-limit handling
* Token and cost budgets
* Detection of repeated tool calls
* Configurable command allowlists
* Automatic project discovery
* Docker or operating-system-level sandboxing
* Packaging as an installable CLI
* Support for additional programming languages

## Development Workflow

Create a feature branch:

```bash
git switch -c feature/my-change
```

Make and test changes.

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
* New-file generation
* Controlled subprocess execution
* Runtime configuration
* Prompt design for coding agents

It is intended for learning and experimentation.

## License

This project is currently provided for educational purposes.

Add a license file before redistributing it or using it as the basis of a production project.

## Author

Created by [cyberbotsaber](https://github.com/cyberbotsaber).
