from ecr_cleaner import Repository


def main() -> None:
    """Functional test that ensures the library can be imported and utilized"""
    Repository(name=None, region=None)

    print("OK.")


if __name__ == "__main__":
    main()
