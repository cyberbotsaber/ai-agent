from functions.run_command import run_command


def assert_contains(result: str, expected: str) -> None:
    assert expected in result, (
        f"Expected {expected!r} in result:\n{result}"
    )


def main() -> None:
    print("Test pwd")
    pwd_result = run_command(".", ["pwd"])
    assert_contains(pwd_result, "STDOUT:")
    print("PASS")

    print("Test pwd with arguments")
    pwd_argument_result = run_command(".", ["pwd", "--help"])
    assert_contains(
        pwd_argument_result,
        "pwd does not accept arguments",
    )
    print("PASS")

    print("Test ls current directory")
    ls_result = run_command(".", ["ls", "-la", "."])
    assert_contains(ls_result, "STDOUT:")
    print("PASS")

    print("Test ls outside working directory")
    outside_ls_result = run_command(".", ["ls", "/"])
    assert_contains(
        outside_ls_result,
        "outside the permitted working directory",
    )
    print("PASS")

    print("Test unsafe ls option")
    unsafe_ls_result = run_command(
        ".",
        ["ls", "--recursive", "."],
    )
    assert_contains(
        unsafe_ls_result,
        "is not allowed",
    )
    print("PASS")

    print("Test git status")
    git_status_result = run_command(".", ["git", "status"])
    assert_contains(git_status_result, "STDOUT:")
    print("PASS")

    print("Test git diff")
    git_diff_result = run_command(".", ["git", "diff"])
    assert (
        "STDOUT:" in git_diff_result
        or "No output produced" in git_diff_result
    )
    print("PASS")

    print("Test current branch")
    branch_result = run_command(
        ".",
        ["git", "branch", "--show-current"],
    )
    assert_contains(branch_result, "STDOUT:")
    print("PASS")

    print("Test destructive Git command")
    reset_result = run_command(
        ".",
        ["git", "reset", "--hard"],
    )
    assert_contains(
        reset_result,
        'Git subcommand "reset" is not allowed',
    )
    print("PASS")

    print("Test Git clean")
    clean_result = run_command(
        ".",
        ["git", "clean", "-fd"],
    )
    assert_contains(
        clean_result,
        'Git subcommand "clean" is not allowed',
    )
    print("PASS")

    print("All command safety tests passed.")


if __name__ == "__main__":
    main()
