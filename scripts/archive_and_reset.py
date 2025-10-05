import json, random, os, datetime, time
from github import Github

rows = "ABCDEFGHIJ"
cols = [str(i) for i in range(1, 11)]
ships_config = {"carrier": 5, "battleship": 4, "submarine": 3, "destroyer": 2, "patrol": 2}

# Place ships randomly
def place_ship(size, occupied):
    while True:
        orientation = random.choice(["H", "V"])
        row = random.choice(rows)
        col = random.choice(cols)
        if orientation == "H":
            start = int(col)
            if start + size - 1 > 10: continue
            cells = [row + str(start + i) for i in range(size)]
        else:
            start = rows.index(row)
            if start + size - 1 > 9: continue
            cells = [rows[start + i] + col for i in range(size)]
        if any(cell in occupied for cell in cells): continue
        return cells

# Generate new ships
occupied, ship_map = set(), {}
for name, size in ships_config.items():
    cells = place_ship(size, occupied)
    for cell in cells:
        ship_map[cell] = name
        occupied.add(cell)

with open("game/ships.json", "w") as f:
    json.dump(ship_map, f, indent=2)

# Load previous board and leaderboard
try:
    with open("game/board.json", "r") as f: board = json.load(f)
    with open("game2/leaderboard.json", "r") as f: leaderboard = json.load(f)
except FileNotFoundError:
    board, leaderboard = {}, {}

# Reveal ships on board
revealed_board = board.copy()
for coord in ship_map:
    if revealed_board.get(coord) == "":
        revealed_board[coord] = "🚢"

# Determine winner
winner_id = None
for player, stats in leaderboard.items():
    if stats["hits"] >= len(ship_map):
        winner_id = player
        break

winner_name = leaderboard.get(winner_id, {}).get("username", f"user-{winner_id}") if winner_id else None

# Archive round
timestamp = datetime.datetime.utcnow().isoformat()
round_data = {
    "timestamp": timestamp,
    "winner": winner_name,
    "board": board,
    "revealed_board": revealed_board,
    "leaderboard": leaderboard
}
os.makedirs("rounds", exist_ok=True)
existing = [f for f in os.listdir("rounds") if f.startswith("round_")]
next_num = len(existing) + 1
with open(f"rounds/round_{next_num:03}.json", "w") as f:
    json.dump(round_data, f, indent=2)

# Reset board and leaderboard
board = {r + c: "" for r in rows for c in cols}
with open("game/board.json", "w") as f:
    json.dump(board, f, indent=2)
with open("game2/leaderboard.json", "w") as f:
    json.dump({}, f, indent=2)

# Update README history
summary = f"- Round {next_num:03} ({timestamp[:10]}): 🏆 Winner — `@{winner_name}`" if winner_name else f"- Round {next_num:03} ({timestamp[:10]}): No winner"
with open("README.md", "r") as f: readme = f.read()
start = readme.find("<!-- HISTORY_START -->")
end = readme.find("<!-- HISTORY_END -->") + len("<!-- HISTORY_END -->")
history = readme[start:end]
updated_history = history.replace("<!-- HISTORY_START -->", f"<!-- HISTORY_START -->\n{summary}")
readme = readme[:start] + updated_history + readme[end:]
with open("README.md", "w") as f: f.write(readme)

# GitHub comment and close
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("GITHUB_REPOSITORY")
ISSUE_NUMBER = int(os.getenv("ISSUE_NUMBER"))
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)
issue = repo.get_issue(number=ISSUE_NUMBER)
issue.create_comment("🔄 Game has been reset! Ships repositioned, board cleared, leaderboard wiped, and round archived.")
time.sleep(30)
issue.edit(state="closed")
