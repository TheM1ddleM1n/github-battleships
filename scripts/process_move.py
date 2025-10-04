import os
import json
import re
from github import Github

# Load environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("GITHUB_REPOSITORY")
ISSUE_NUMBER = int(os.getenv("ISSUE_NUMBER"))

# Connect to GitHub
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)
issue = repo.get_issue(number=ISSUE_NUMBER)
username = issue.user.login

# Extract move from issue title
match = re.match(r"Move:\s*([A-J](?:10|[1-9]))", issue.title.strip(), re.IGNORECASE)
if not match:
    issue.create_comment("❌ Invalid move format. Use `Move: B4`.")
    exit()

move = match.group(1).upper()

# Load board
with open("game/board.json", "r") as f:
    board = json.load(f)

# Load ships
with open("game/ships.json", "r") as f:
    ships = json.load(f)

# Process move
if move not in board:
    issue.create_comment(f"❌ `{move}` is not a valid cell.")
    exit()

if board[move] != "":
    issue.create_comment(f"⚠️ `{move}` was already played and marked as `{board[move]}`.")
    exit()

# Determine hit or miss
if move in ships:
    board[move] = "X"
    ship_hit = ships[move]
    result = f"💥 Hit by @{username}! `{move}` struck the `{ship_hit}`!"
else:
    board[move] = "O"
    result = f"🌊 `{move}` is a **Miss**."

# Update board
with open("game/board.json", "w") as f:
    json.dump(board, f, indent=2)

# Update leaderboard
try:
    with open("game/leaderboard.json", "r") as f:
        leaderboard = json.load(f)
except FileNotFoundError:
    leaderboard = {}

player = leaderboard.get(username, {"hits": 0, "misses": 0, "streak": 0})
if board[move] == "X":
    player["hits"] += 1
    player["streak"] += 1
else:
    player["misses"] += 1
    player["streak"] = 0

total = player["hits"] + player["misses"]
player["accuracy"] = round(player["hits"] / total, 2) if total else 0.0
leaderboard[username] = player

with open("game/leaderboard.json", "w") as f:
    json.dump(leaderboard, f, indent=2)

# Victory detection
all_ship_cells = set(ships.keys())
hit_cells = {cell for cell, mark in board.items() if mark == "X"}

if all_ship_cells.issubset(hit_cells):
    issue.create_comment(f"🎉 `{username}` has sunk all ships and **won the game**! 🏆")

# Comment result
issue.create_comment(result)

# Render board as markdown table
def render_board(board):
    header = "|   | " + " | ".join(str(i) for i in range(1, 11)) + " |\n"
    divider = "|---|" + "---|" * 10 + "\n"
    rows = ""
    for row in "ABCDEFGHIJ":
        cells = [board.get(f"{row}{col}", " ") or " " for col in range(1, 11)]
        rows += f"| {row} | " + " | ".join(cells) + " |\n"
    return header + divider + rows

# Render leaderboard with medals and emojis
def render_leaderboard(leaderboard):
    header = "| Rank | Player | 🏹 Hits | 💦 Misses | 🎯 Accuracy | 🔥 Streak |\n"
    divider = "|------|--------|----------|------------|--------------|------------|\n"
    rows = ""

    sorted_players = sorted(
        leaderboard.items(),
        key=lambda x: (x[1]["hits"], x[1]["accuracy"]),
        reverse=True
    )

    for i, (player, stats) in enumerate(sorted_players, start=1):
        if i == 1:
            rank = "🥇"
        elif i == 2:
            rank = "🥈"
        elif i == 3:
            rank = "🥉"
        else:
            rank = f"{i}"
        row = f"| {rank} | {player} | {stats['hits']} | {stats['misses']} | {stats['accuracy']} | {stats['streak']} |\n"
        rows += row

    return header + divider + rows

# Update README
with open("README.md", "r") as f:
    readme = f.read()

# Update board section
start = readme.find("<!-- BOARD_START -->")
end = readme.find("<!-- BOARD_END -->") + len("<!-- BOARD_END -->")
new_board = render_board(board)
readme = readme[:start] + "<!-- BOARD_START -->\n" + new_board + readme[end - len("<!-- BOARD_END -->"):]

# Update leaderboard section
lb_start = readme.find("<!-- LEADERBOARD_START -->")
lb_end = readme.find("<!-- LEADERBOARD_END -->") + len("<!-- LEADERBOARD_END -->")
new_leaderboard = render_leaderboard(leaderboard)
readme = readme[:lb_start] + "<!-- LEADERBOARD_START -->\n" + new_leaderboard + readme[lb_end - len("<!-- LEADERBOARD_END -->"):]

with open("README.md", "w") as f:
    f.write(readme)
