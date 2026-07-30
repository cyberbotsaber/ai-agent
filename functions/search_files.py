import os


MAX_RESULTS = 100
MAX_FILE_SIZE = 1_000_000

IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
}


schema_search_files = {
    "type": "function",
    "function": {
        "name": "search_files",
        "description": (
            "Searches text files inside the working directory for a text query "
            "and returns matching file paths and line numbers"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Text to search for",
                },
                "directory": {
                    "type": "string",
                    "description": (
                        "Directory to search, relative to the working directory. "
                        "Defaults to the project root."
                    ),
                },
            },
            "required": ["query"],
        },
    },
}


def search_files(
    working_directory: str,
    query: str,
    directory: str = ".",
) -> str:
    try:
        working_dir_abs = os.path.realpath(working_directory)
        target_dir = os.path.realpath(
            os.path.join(working_dir_abs, directory)
        )

        valid_target = (
            os.path.commonpath([working_dir_abs, target_dir])
            == working_dir_abs
        )

        if not valid_target:
            return (
                f'Error: Cannot search "{directory}" as it is outside '
                "the permitted working directory"
            )

        if not os.path.isdir(target_dir):
            return f'Error: "{directory}" is not a directory'

        if not query:
            return "Error: Search query cannot be empty"

        results: list[str] = []

        for root, dir_names, file_names in os.walk(target_dir):
            dir_names[:] = [
                name
                for name in dir_names
                if name not in IGNORED_DIRECTORIES
            ]

            for file_name in file_names:
                file_path = os.path.join(root, file_name)

                if os.path.getsize(file_path) > MAX_FILE_SIZE:
                    continue

                try:
                    with open(
                        file_path,
                        "r",
                        encoding="utf-8",
                    ) as file:
                        for line_number, line in enumerate(file, start=1):
                            if query.lower() in line.lower():
                                relative_path = os.path.relpath(
                                    file_path,
                                    working_dir_abs,
                                )

                                results.append(
                                    f"{relative_path}:{line_number}: "
                                    f"{line.rstrip()}"
                                )

                                if len(results) >= MAX_RESULTS:
                                    results.append(
                                        f"...Search stopped after "
                                        f"{MAX_RESULTS} matches"
                                    )
                                    return "\n".join(results)

                except (UnicodeDecodeError, PermissionError):
                    continue

        if not results:
            return f'No matches found for "{query}"'

        return "\n".join(results)

    except Exception as error:
        return f"Error: {error}"
