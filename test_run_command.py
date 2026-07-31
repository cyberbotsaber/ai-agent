from functions.run_command import run_command


def main() -> None:
    print("Run calculator tests:")
    print(
        run_command(
            "calculator",
            ["python", "tests.py"],
        )
    )

    print("\nRun disallowed command:")
    print(
        run_command(
            "calculator",
            ["rm", "-rf", "."],
        )
    )

    print("\nRun Python version:")
    print(
        run_command(
            "calculator",
            ["python", "--version"],
        )
    )


if __name__ == "__main__":
    main()
