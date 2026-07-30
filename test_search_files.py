from functions.search_files import search_files


def main() -> None:
    print("Search for Calculator:")
    print(search_files("calculator", "Calculator"))

    print("\nSearch for format_json_output:")
    print(search_files("calculator", "format_json_output"))

    print("\nAttempt directory escape:")
    print(search_files("calculator", "root", "../"))


if __name__ == "__main__":
    main()
