#!/usr/bin/env python3

import subprocess
from pathlib import Path


def update_build_hash():
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            commit_hash = result.stdout.strip()
        else:
            print("Warning: Could not get git commit hash")
            return
    except Exception as e:
        print(f"Warning: Failed to get git commit hash: {e}")
        return

    build_info_path = Path(__file__).parent.parent / "autohack" / "core" / "build.py"
    content = build_info_path.read_text()

    lines = content.split("\n")
    updated_lines = []
    for line in lines:
        if line.startswith("BUILD_COMMIT_HASH = "):
            updated_lines.append(f'BUILD_COMMIT_HASH = "{commit_hash}"')
        else:
            updated_lines.append(line)

    build_info_path.write_text("\n".join(updated_lines))
    print(f"Updated BUILD_COMMIT_HASH to {commit_hash}")


if __name__ == "__main__":
    update_build_hash()
