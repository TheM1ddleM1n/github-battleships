import json
import os
import time
import random
from github import Github

# To Setup GitHub
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("GITHUB_REPOSITORY")
ISSUE_NUMBER = int(os.getenv("ISSUE_NUMBER"))

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)
issue = repo.get_issue(number=ISSUE_NUMBER)

rows = "ABCDEFGHIJ"
cols = [str(i) for i in range(1, 11)]
ships_config = {"carrier": 5, "battleship": 4, "submarine": 3, "destroyer": 2, "patrol": 2}

# Place ships in random positions
def place_ship(size, occupied):
    max_attempts = 100
    attempts = 0
    while attempts < max_attempts:
        attempts += 1
        orientation = random.choice(["H", "V"])
        row = random.choice(rows)
        col = random.choice(cols)
        
        if orientation == "H":
            start = int(col)
            if start + size - 1 > 10:
                continue
            cells = [row + str(start + i) for i in range(size)]
        else:
            start = rows.index(row)
            if start + size - 1 > 9:
                continue
            cells = [rows[start + i] + col for i in range(size)]
        
        if any(cell in occupied for cell in cells):
            continue
            
        return cells
    
    raise Exception(f"Could not place ship of size {size} after {max_attempts} attempts")

# Generate new ships according to if it is occupied or not!
occupied = set()
ship_map = {}

try:
    for name, size in ships_config.items():
        cells = place_ship(size, occupied)
        for cell in cells:
            ship_map[cell] = name
            occupied.add(cell)
    
    issue.create_comment(f"✅ Successfully generated new ship positions ({len(ship_map)} cells)")
except Exception as e:
    issue.create_comment(f"❌ Error generating ships: {str(e)}")
    exit(1)

# Create the needed directories if they do not exist.
os.makedirs("game", exist_ok=True)
os.makedirs("game2", exist_ok=True)

# Save the new ships positions to game/ships.json
with open("game/ships.json", "w") as f:
    json.dump(ship_map, f, indent=2)

# Reset board after all spaces filled
board = {r + c: "" for r in rows for c in cols}
with open("game/board.json", "w") as f:
    json.dump(board, f, indent=2)

# Reset current game leaderboard and the move history from players of that match
with open("game2/leaderboard.json", "w") as f:
    json.dump({}, f, indent=2)

with open("game2/move_history.json", "w") as f:
    json.dump([], f, indent=2)

# Keep all-time leaderboard and achievements intact
# Just to make sure they exist
if not os.path.exists("game2/all_time_leaderboard.json"):
    with open("game2/all_time_leaderboard.json", "w") as f:
        json.dump({}, f, indent=2)

if not os.path.exists("game2/achievements.json"):
    with open("game2/achievements.json", "w") as f:
        json.dump({}, f, indent=2)

# Update README
def render_board_reset():
    header = "|   | " + " | ".join(str(i) for i in range(1, 11)) + " |\n"
    divider = "|---|" + "---|" * 10 + "\n"
    rows_str = ""
    for row in "ABCDEFGHIJ":
        cells = ["⬜"] * 10
        rows_str += f"| {row} | " + " | ".join(cells) + " |\n"
    return header + divider + rows_str

def render_ship_status_reset():
    status_text = "### 🚢 Fleet Status\n\n"
    ships_info = [
        ("🛳️", "CARRIER", 5),
        ("⚓", "BATTLESHIP", 4),
        ("🔱", "SUBMARINE", 3),
        ("⛴️", "DESTROYER", 2),
        ("🛥️", "PATROL", 2)
    ]
    for emoji, name, size in ships_info:
        status_text += f"- {emoji} **{name}** ({size} cells): ✅ Afloat\n"
    return status_text

def render_game_stats_reset():
    stats_text = "### 📊 Game Statistics\n\n"
    stats_text += f"- 🎯 **Ship Cells Remaining:** 16/16\n"
    stats_text += f"- 🎲 **Total Moves:** 0\n"
    stats_text += f"- 💥 **Total Hits:** 0\n"
    stats_text += f"- 🌊 **Total Misses:** 0\n"
    stats_text += f"- 📈 **Community Accuracy:** 0.0%\n"
    stats_text += f"- 👥 **Active Players:** 0\n"
    return stats_text

def render_move_history_reset():
    return "### 📜 Recent Moves\n\n*No moves yet! Be the first to fire!*\n"

def render_leaderboard_reset():
    header = "| Rank | Player | 🖼️ Avatar | 🏹 Hits | 💦 Misses | 🎯 Accuracy | 🔥 Streak | 🚢 Sunk |\n"
    divider = "|------|--------|-----------|----------|------------|--------------|------------|----------|\n"
    return header + divider + "| - | *No players yet* | - | - | - | - | - | - |\n"

# Read and update README
try:
    with open("README.md", "r") as f:
        readme = f.read()
except FileNotFoundError:
    issue.create_comment("❌ ERROR: README.md not found!")
    exit(1)

# Update board.
start = readme.find("<!-- BOARD_START -->")
end = readme.find("<!-- BOARD_END -->")
if start != -1 and end != -1:
    end += len("<!-- BOARD_END -->")
    readme = readme[:start] + "<!-- BOARD_START -->\n" + render_board_reset() + "<!-- BOARD_END -->" + readme[end:]

# Update ship status.
ship_start = readme.find("<!-- SHIP_STATUS_START -->")
ship_end = readme.find("<!-- SHIP_STATUS_END -->")
if ship_start != -1 and ship_end != -1:
    ship_end += len("<!-- SHIP_STATUS_END -->")
    readme = readme[:ship_start] + "<!-- SHIP_STATUS_START -->\n" + render_ship_status_reset() + "<!-- SHIP_STATUS_END -->" + readme[ship_end:]

# Update game stats.
stats_start = readme.find("<!-- GAME_STATS_START -->")
stats_end = readme.find("<!-- GAME_STATS_END -->")
if stats_start != -1 and stats_end != -1:
    stats_end += len("<!-- GAME_STATS_END -->")
    readme = readme[:stats_start] + "<!-- GAME_STATS_START -->\n" + render_game_stats_reset() + "<!-- GAME_STATS_END -->" + readme[stats_end:]

# Update move history.
hist_start = readme.find("<!-- HISTORY_MOVES_START -->")
hist_end = readme.find("<!-- HISTORY_MOVES_END -->")
if hist_start != -1 and hist_end != -1:
    hist_end += len("<!-- HISTORY_MOVES_END -->")
    readme = readme[:hist_start] + "<!-- HISTORY_MOVES_START -->\n" + render_move_history_reset() + "<!-- HISTORY_MOVES_END -->" + readme[hist_end:]

# Update current game leaderboard.
lb_start = readme.find("<!-- LEADERBOARD_START -->")
lb_end = readme.find("<!-- LEADERBOARD_END -->")
if lb_start != -1 and lb_end != -1:
    lb_end += len("<!-- LEADERBOARD_END -->")
    readme = readme[:lb_start] + "<!-- LEADERBOARD_START -->\n" + render_leaderboard_reset() + "<!-- LEADERBOARD_END -->" + readme[lb_end:]

# Write updated README.
with open("README.md", "w") as f:
    f.write(readme)

# Display new ship positions (for manual secret update)
ship_json_str = json.dumps(ship_map, indent=2)
issue.create_comment(
    "🔄 **Manual Game Reset Complete!**\n\n"
    "✅ New ships generated and positioned\n"
    "✅ Board cleared\n"
    "✅ Current game leaderboard reset\n"
    "✅ Move history cleared\n"
    "✅ All-time stats and achievements preserved\n\n"
    "⚠️ **IMPORTANT:** You need to manually update the `SHIPS_JSON` secret:\n\n"
    "1. Go to Settings → Secrets and variables → Actions\n"
    "2. Update `SHIPS_JSON` with the following content:\n\n"
    "```json\n" + ship_json_str + "\n```\n\n"
    "🎯 Once secret is updated, the game is ready!"
)

# Finally, closes the issue (move) after 30 seconds has passed!
time.sleep(30)
issue.edit(state="closed")

print("Manual reset completed successfully!")
print(f"New ship positions saved to game/ships.json")
print("Remember to update SHIPS_JSON secret manually!")
