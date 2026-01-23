import sys


def main():
    if len(sys.argv) != 2:
        print("Usage: python get_executable_version.py <version>")
        sys.exit(1)

    inputVer = sys.argv[1]

    versionParts = inputVer.split(".")
    if len(versionParts) < 3:
        versionParts += ["0"] * (3 - len(versionParts))
    elif len(versionParts) > 3:
        versionParts = versionParts[:3]

    print(".".join(versionParts))


if __name__ == "__main__":
    main()
