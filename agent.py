from typing import Any

from openai import OpenAI

from call_function import available_functions, call_function


class Agent:
    def __init__(
        self,
        client: OpenAI,
        model: str,
        working_directory: str,
        max_iterations: int = 20,
        verbose: bool = False,
    ) -> None:
        self.client = client
        self.model = model
        self.working_directory = working_directory
        self.max_iterations = max_iterations
        self.verbose = verbose

    def run(self, messages: list[Any]) -> str:
        for _ in range(self.max_iterations):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=available_functions,
                temperature=0,
            )

            if response.usage is None:
                raise RuntimeError(
                    "The API response did not include token usage information."
                )

            if self.verbose:
                print(f"Prompt tokens: {response.usage.prompt_tokens}")
                print(
                    f"Response tokens: "
                    f"{response.usage.completion_tokens}"
                )

            message = response.choices[0].message

            if not message.tool_calls and not message.content:
                if self.verbose:
                    finish_reason = response.choices[0].finish_reason
                    print(
                        "Model returned no content or tool calls. "
                        f"Retrying. Finish reason: {finish_reason}"
                    )
                continue

            messages.append(message)

            if message.tool_calls:
                for tool_call in message.tool_calls:
                    result_message = call_function(
                        tool_call,
                        working_directory=self.working_directory,
                        verbose=self.verbose,
                    )

                    if not result_message.get("content"):
                        raise RuntimeError(
                            "Function call returned an empty result."
                        )

                    if self.verbose:
                        print(f"-> {result_message['content']}")

                    messages.append(result_message)

                continue

            return message.content or ""

        raise RuntimeError(
            "Agent reached the maximum number of iterations "
            "without producing a final response."
        )
