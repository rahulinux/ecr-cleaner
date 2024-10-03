from template_package import hello_world


def main() -> None:
    """Functional test that ensures the library can be imported and utilized"""
    hello_world()

    print("OK.")


if __name__ == "__main__":
    main()
