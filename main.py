import argparse
import os

from dotenv import load_dotenv
from openai import OpenAI

from call_function import available_functions, call_function
from prompts import system_prompt


load_dotenv()

api_key = os.environ.get("OPENROUTER_API_KEY")

if api_key is None:
    raise RuntimeError(
        "OPENROUTER_API_KEY was not found. Add it to your .env file."
    )

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)


def generate_content(
    client: OpenAI,
    messages: list,
    verbose: bool,
) -> None:
    for _ in range(20):
        response = client.chat.completions.create(
            model="openrouter/free",
            messages=messages,
            tools=available_functions,
            temperature=0,
        )

        if response.usage is None:
            raise RuntimeError(
                "The API response did not include token usage information."
            )

        if verbose:
            print(f"Prompt tokens: {response.usage.prompt_tokens}")
            print(f"Response tokens: {response.usage.completion_tokens}")

        message = response.choices[0].message

        # Occasionally, a routed model may return neither text nor tool calls.
        # Retry without adding the empty response to the conversation history.
        if not message.tool_calls and not message.content:
            if verbose:
                finish_reason = response.choices[0].finish_reason
                print(
                    "Model returned no content or tool calls. "
                    f"Retrying. Finish reason: {finish_reason}"
                )
            continue

        # Preserve the assistant response, including any tool calls.
        messages.append(message)

        if message.tool_calls:
            for tool_call in message.tool_calls:
                result_message = call_function(
                    tool_call,
                    verbose=verbose,
                )

                if not result_message.get("content"):
                    raise RuntimeError(
                        "Function call returned an empty result."
                    )

                if verbose:
                    print(f"-> {result_message['content']}")

                # Return the tool result to the model on the next iteration.
                messages.append(result_message)

            continue

        print("Final response:")
        print(message.content)
        return

    raise RuntimeError(
        "Agent reached the maximum number of iterations "
        "without producing a final response."
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="AI coding agent"
    )

    parser.add_argument(
        "user_prompt",
        help="Prompt to send to the model",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    if args.verbose:
        print(f"User prompt: {args.user_prompt}")

    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": args.user_prompt,
        },
    ]

    generate_content(
        client,
        messages,
        args.verbose,
    )


if __name__ == "__main__":
    main()
