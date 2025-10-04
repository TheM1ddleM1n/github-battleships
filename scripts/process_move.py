import os
import json
import re
from github import Github
from random import choice

# Load environment variables
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

# Process move
if move not in board:
    issue.create_comment(f"❌ `{move}` is not a valid cell.")
elif board[move] == "":
    result = choice(["X", "O"])  # Simulate hit/miss
    board[move] = result
    with open("game/board.json", "w") as f:
        json.dump(board, f, indent=2)
    emoji = "💥" if result == "X" else "🌊"
    issue.create_comment(f"{emoji} `{move}` is a **{'Hit' if result == 'X' else 'Miss'}**!")
else:
    issue.create_comment(f"⚠️ `{move}` was already played and marked as `{board[move]}`.")

# Render board as markdown table
def render_board(board):
    header = "|   | " + " | ".join(str(i) for i in range(1, 11)) + " |\n"
    divider = "|---|" + "---|" * 10 + "\n"
    rows = ""
    for row in "ABCDEFGHIJ":
        cells = [board.get(f"{row}{col}", " ") or " " for col in range(1, 11)]
        rows += f"| {row} | " + " | ".join(cells) + " |\n"
    return header + divider + rows

# Update README.md
with open("README.md", "r") as f:
    readme = f.read()

start = readme.find("<!-- BOARD_START -->")
end = readme.find("<!-- BOARD_END -->") + len("<!-- BOARD_END -->")
new_board = render_board(board)
updated = readme[:start] + "<!-- BOARD_START -->\n" + new_board + readme[end - len("<!-- BOARD_END -->"):]

with open("README.md", "w") as f:
    f.write(updated)
