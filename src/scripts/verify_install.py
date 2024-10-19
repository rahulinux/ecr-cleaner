from ecr_lifecycle import Repository


def main() -> None:
    """Functional test that ensures the library can be imported and utilized"""
    Repository()

    print("OK.")


if __name__ == "__main__":
    main()
