import json, random, os
from github import Github

rows = "ABCDEFGHIJ"
cols = [str(i) for i in range(1, 11)]
ships = {"carrier": 5, "battleship": 4, "submarine": 3, "destroyer": 2, "patrol": 2}

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

occupied, ship_map = set(), {}
for name, size in ships.items():
    cells = place_ship(size, occupied)
    for cell in cells:
        ship_map[cell] = name
        occupied.add(cell)

with open("game/ships.json", "w") as f:
    json.dump(ship_map, f, indent=2)

board = {r + c: "" for r in rows for c in cols}
with open("game/board.json", "w") as f:
    json.dump(board, f, indent=2)

with open("game/leaderboard.json", "w") as f:
    json.dump({}, f, indent=2)

# Comment confirmation
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("REPO_NAME")
ISSUE_NUMBER = int(os.getenv("ISSUE_NUMBER"))
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)
issue = repo.get_issue(number=ISSUE_NUMBER)
issue.create_comment("🔄 Game has been reset! Ships repositioned, board cleared, and leaderboard wiped. Ready for battle!")
