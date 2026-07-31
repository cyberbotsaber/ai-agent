import argparse
import os

from dotenv import load_dotenv
from openai import OpenAI

from agent import Agent
from prompts import system_prompt
from settings import load_settings


load_dotenv()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="AI coding agent"
    )

    parser.add_argument(
        "user_prompt",
        help="Prompt to send to the model",
    )

    parser.add_argument(
        "--working-directory",
        default=".",
        help=(
            "Root directory of the Python project the agent may access. "
            "Defaults to the current directory."
        ),
    )

    parser.add_argument(
        "--model",
        default=None,
        help="Model ID. Overrides AI_AGENT_MODEL.",
    )

    parser.add_argument(
        "--base-url",
        default=None,
        help="OpenAI-compatible API base URL.",
    )

    parser.add_argument(
        "--max-iterations",
        type=int,
        default=None,
        help="Maximum number of model iterations.",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    settings = load_settings(
        model_override=args.model,
        base_url_override=args.base_url,
        max_iterations_override=args.max_iterations,
    )

    client = OpenAI(
        base_url=settings.base_url,
        api_key=settings.api_key,
    )

    working_directory = os.path.abspath(
        args.working_directory
    )

    if not os.path.isdir(working_directory):
        raise RuntimeError(
            f'Working directory does not exist or is not a directory: '
            f'"{args.working_directory}"'
        )

    if args.verbose:
        print(f"User prompt: {args.user_prompt}")
        print(f"Working directory: {working_directory}")
        print(f"Model: {settings.model}")
        print(f"Base URL: {settings.base_url}")
        print(f"Maximum iterations: {settings.max_iterations}")

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

    agent = Agent(
        client=client,
        model=settings.model,
        working_directory=working_directory,
        max_iterations=settings.max_iterations,
        verbose=args.verbose,
    )

    final_response = agent.run(messages)

    print("Final response:")
    print(final_response)


if __name__ == "__main__":
    main()
