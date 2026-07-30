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
}


schema_run_command = {
    "type": "function",
    "function": {
        "name": "run_command",
        "description": (
            "Runs an approved development command inside the working directory. "
            "Useful for tests, linters, type checks, and Python modules."
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
                        '["uv", "run", "pytest"]'
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

        executable = command[0]

        if executable not in ALLOWED_COMMANDS:
            return (
                f'Error: Command "{executable}" is not allowed. '
                f"Allowed commands: {', '.join(sorted(ALLOWED_COMMANDS))}"
            )

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
    except Exception as error:
        return f"Error: executing command: {error}"
