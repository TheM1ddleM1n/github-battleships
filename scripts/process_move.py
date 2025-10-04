import os
import json
import re
from github import Github

# Load GitHub token and repo info
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("GITHUB_REPOSITORY")
ISSUE_NUMBER = int(os.getenv("ISSUE_NUMBER"))

# Connect to GitHub
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)
issue = repo.get_issue(number=ISSUE_NUMBER)

# Extract move from issue title
match = re.match(r"Move:\s*([A-J](?:10|[1-9]))", issue.title.strip(), re.IGNORECASE)
if not match:
    issue.create_comment("❌ Invalid move format. Use `Move: B4`.")
    exit()

move = match.group(1).upper()

# Load board
with open("game/board.json", "r") as f:
    board = json.load(f)

# Check move status
if move not in board:
    issue.create_comment(f"❌ `{move}` is not a valid cell.")
elif board[move] == "":
    # Randomly simulate hit/miss (replace with real ship logic later)
    from random import choice
    result = choice(["X", "O"])
    board[move] = result
    with open("game/board.json", "w") as f:
        json.dump(board, f, indent=2)
    emoji = "💥" if result == "X" else "🌊"
    issue.create_comment(f"{emoji} `{move}` is a **{'Hit' if result == 'X' else 'Miss'}**!")
else:
    issue.create_comment(f"⚠️ `{move}` was already played and marked as `{board[move]}`.")

