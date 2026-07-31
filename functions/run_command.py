import os
import subprocess


DEFAULT_TIMEOUT_SECONDS = 30
MAX_TIMEOUT_SECONDS = 120

ALLOWED_COMMANDS = {
    "python",
    "python3",
    "uv",
    "pytest",
    "ruff",
    "mypy",
    "pwd",
    "ls",
    "git",
}

ALLOWED_GIT_COMMANDS = {
    "status",
    "diff",
    "log",
}


schema_run_command = {
    "type": "function",
    "function": {
        "name": "run_command",
        "description": (
            "Runs an approved development command inside the working directory. "
            "Useful for tests, linting, type checking, project inspection, and "
            "read-only Git operations."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                    "description": (
                        "Command and arguments as a list of strings, for example "
                        '["uv", "run", "pytest"] or ["git", "status"]'
                    ),
                },
                "timeout_seconds": {
                    "type": "integer",
                    "description": (
                        "Maximum execution time in seconds. "
                        "Defaults to 30 and cannot exceed 120."
                    ),
                },
            },
            "required": ["command"],
        },
    },
}


def is_path_inside_working_directory(
    working_directory: str,
    path_argument: str,
) -> bool:
    """Return True when a path resolves inside the permitted workspace."""
    target_path = os.path.realpath(
        os.path.join(working_directory, path_argument)
    )

    try:
        return (
            os.path.commonpath([working_directory, target_path])
            == working_directory
        )
    except ValueError:
        return False


def validate_ls_command(
    working_directory: str,
    command: list[str],
) -> str | None:
    """Validate ls flags and path arguments."""
    allowed_flags = {
        "-a",
        "-l",
        "-la",
        "-al",
        "-h",
        "-lh",
        "-hl",
        "-lah",
        "-alh",
        "--all",
        "--long",
        "--human-readable",
    }

    for argument in command[1:]:
        if argument.startswith("-"):
            if argument not in allowed_flags:
                return f'Error: ls option "{argument}" is not allowed'
            continue

        if not is_path_inside_working_directory(
            working_directory,
            argument,
        ):
            return (
                f'Error: ls path "{argument}" is outside '
                "the permitted working directory"
            )

    return None


def validate_git_command(command: list[str]) -> str | None:
    """Allow only specific read-only Git operations."""
    if len(command) < 2:
        return "Error: A Git subcommand is required"

    subcommand = command[1]

    if subcommand in ALLOWED_GIT_COMMANDS:
        return None

    if subcommand == "branch":
        if command[2:] == ["--show-current"]:
            return None

        return (
            'Error: Only "git branch --show-current" is allowed'
        )

    return (
        f'Error: Git subcommand "{subcommand}" is not allowed. '
        "Allowed Git operations are status, diff, log, "
        "and branch --show-current"
    )


def validate_command(
    working_directory: str,
    command: list[str],
) -> str | None:
    """Apply command-specific safety rules."""
    executable = command[0]

    if executable not in ALLOWED_COMMANDS:
        return (
            f'Error: Command "{executable}" is not allowed. '
            f"Allowed commands: {', '.join(sorted(ALLOWED_COMMANDS))}"
        )

    if executable == "pwd":
        if len(command) != 1:
            return "Error: pwd does not accept arguments"
        return None

    if executable == "ls":
        return validate_ls_command(
            working_directory,
            command,
        )

    if executable == "git":
        return validate_git_command(command)

    return None


def run_command(
    working_directory: str,
    command: list[str],
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> str:
    try:
        working_dir_abs = os.path.realpath(working_directory)

        if not os.path.isdir(working_dir_abs):
            return (
                "Error: Working directory does not exist "
                "or is not a directory"
            )

        if not command:
            return "Error: Command cannot be empty"

        if not all(
            isinstance(argument, str)
            for argument in command
        ):
            return "Error: Every command argument must be a string"

        validation_error = validate_command(
            working_dir_abs,
            command,
        )

        if validation_error:
            return validation_error

        if timeout_seconds <= 0:
            return "Error: Timeout must be greater than zero"

        if timeout_seconds > MAX_TIMEOUT_SECONDS:
            return (
                f"Error: Timeout cannot exceed "
                f"{MAX_TIMEOUT_SECONDS} seconds"
            )

        completed_process = subprocess.run(
            command,
            cwd=working_dir_abs,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            shell=False,
        )

        output: list[str] = []

        if completed_process.returncode != 0:
            output.append(
                f"Process exited with code "
                f"{completed_process.returncode}"
            )

        if completed_process.stdout:
            output.append(
                f"STDOUT:\n{completed_process.stdout.rstrip()}"
            )

        if completed_process.stderr:
            output.append(
                f"STDERR:\n{completed_process.stderr.rstrip()}"
            )

        if not completed_process.stdout and not completed_process.stderr:
            output.append("No output produced")

        return "\n".join(output)

    except subprocess.TimeoutExpired:
        return (
            f"Error: Command exceeded the "
            f"{timeout_seconds}-second timeout"
        )
    except FileNotFoundError as error:
        return f"Error: Command is not installed: {error.filename}"
    except Exception as error:
        return f"Error: executing command: {error}"
