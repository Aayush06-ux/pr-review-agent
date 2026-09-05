import os
import subprocess
import time

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def create_test_branch():
    """Creates a new git branch with code changes and pushes to GitHub."""
    branch_name = f"test-feature-{int(time.time())}"
    print(f"Creating new test branch: {branch_name}...")

    subprocess.run(["git", "checkout", "main"], cwd=ROOT_DIR, check=True)
    subprocess.run(["git", "checkout", "-b", branch_name], cwd=ROOT_DIR, check=True)

    # Modify test file
    test_file = os.path.join(ROOT_DIR, "test_feature.py")
    with open(test_file, "a", encoding="utf-8") as f:
        f.write(f"\n# Test update at {time.strftime('%H:%M:%S')}\n")

    subprocess.run(["git", "add", "test_feature.py"], cwd=ROOT_DIR, check=True)
    subprocess.run(["git", "commit", "-m", f"Add test code changes for AI review"], cwd=ROOT_DIR, check=True)
    subprocess.run(["git", "push", "-u", "origin", branch_name], cwd=ROOT_DIR, check=True)

    print("\n---------------------------------------------------------")
    print("  👉 CLICK THIS LINK TO OPEN YOUR NEW PULL REQUEST:")
    print(f"  https://github.com/Aayush06-ux/pr-review-agent/pull/new/{branch_name}")
    print("---------------------------------------------------------\n")


if __name__ == "__main__":
    create_test_branch()
