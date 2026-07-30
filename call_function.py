import json
from collections.abc import Callable

from functions.get_file_content import (
    get_file_content,
    schema_get_file_content,
)
from functions.get_files_info import (
    get_files_info,
    schema_get_files_info,
)
from functions.run_python_file import (
    run_python_file,
    schema_run_python_file,
)
from functions.write_file import (
    schema_write_file,
    write_file,
)


available_functions = [
    schema_get_files_info,
    schema_get_file_content,
    schema_run_python_file,
    schema_write_file,
]


function_map: dict[str, Callable[..., str]] = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "run_python_file": run_python_file,
    "write_file": write_file,
}


def call_function(tool_call, verbose: bool = False) -> dict:
    function_name = tool_call.function.name
    raw_arguments = tool_call.function.arguments or "{}"

    try:
        function_args = json.loads(raw_arguments)
    except json.JSONDecodeError as error:
        result = (
            f"Error: Invalid JSON arguments for {function_name}: {error}. "
            f"Arguments received: {raw_arguments}"
        )

        if verbose:
            print(f" - Calling function: {function_name}")
            print(f"   {result}")

        return {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result,
        }

    if not isinstance(function_args, dict):
        return {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": (
                f"Error: Arguments for {function_name} must be a JSON object"
            ),
        }

    if verbose:
        print(f" - Calling function: {function_name}({function_args})")
    else:
        print(f" - Calling function: {function_name}")

    function_to_call = function_map.get(function_name)

    if function_to_call is None:
        return {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": f"Error: Unknown function: {function_name}",
        }

    # Injected here so the model cannot choose another working directory.
    function_args["working_directory"] = "./calculator"

    try:
        result = function_to_call(**function_args)
    except Exception as error:
        result = f"Error: calling function {function_name}: {error}"

    return {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": result,
    }
