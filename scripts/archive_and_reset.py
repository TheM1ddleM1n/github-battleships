import json, random, os, datetime, time
from github import Github, Auth

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

# Load previous data
try:
    with open("game/board.json", "r") as f: 
        board = json.load(f)
    with open("game2/leaderboard.json", "r") as f: 
        leaderboard = json.load(f)
    with open("game2/all_time_leaderboard.json", "r") as f:
        all_time_lb = json.load(f)
    with open("game2/move_history.json", "r") as f:
        move_history = json.load(f)
    with open("game2/achievements.json", "r") as f:
        achievements = json.load(f)
except FileNotFoundError:
    board, leaderboard, all_time_lb, move_history, achievements = {}, {}, {}, [], {}

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

# Update all-time leaderboard with games_played
for player_key in leaderboard.keys():
    if player_key in all_time_lb:
        all_time_lb[player_key]["games_played"] = all_time_lb[player_key].get("games_played", 0) + 1

# Archive round
timestamp = datetime.datetime.utcnow().isoformat()
round_data = {
    "timestamp": timestamp,
    "winner": winner_name,
    "board": board,
    "revealed_board": revealed_board,
    "leaderboard": leaderboard,
    "move_history": move_history,
    "achievements": achievements
}

os.makedirs("rounds", exist_ok=True)
existing = [f for f in os.listdir("rounds") if f.startswith("round_")]
next_num = len(existing) + 1
with open(f"rounds/round_{next_num:03}.json", "w") as f:
    json.dump(round_data, f, indent=2)

# Reset current game data
board = {r + c: "" for r in rows for c in cols}
with open("game/board.json", "w") as f:
    json.dump(board, f, indent=2)
with open("game2/leaderboard.json", "w") as f:
    json.dump({}, f, indent=2)
with open("game2/move_history.json", "w") as f:
    json.dump([], f, indent=2)

# Keep all-time leaderboard and achievements
with open("game2/all_time_leaderboard.json", "w") as f:
    json.dump(all_time_lb, f, indent=2)
with open("game2/achievements.json", "w") as f:
    json.dump(achievements, f, indent=2)

# Update README with reset board
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

# Render all-time leaderboard (keep existing data)
def render_all_time_leaderboard(all_time_lb):
    header = "| Rank | Player | 🏹 Total Hits | 🏆 Wins | 🎮 Games | 🔥 Best Streak | 🚢 Ships Sunk |\n"
    divider = "|------|--------|---------------|---------|----------|----------------|----------------|\n"
    
    if not all_time_lb:
        return header + divider + "| - | *No players yet* | - | - | - | - | - |\n"
    
    rows = ""
    sorted_players = sorted(
        all_time_lb.items(),
        key=lambda x: (x[1]["games_won"], x[1]["total_hits"], x[1]["ships_sunk"]),
        reverse=True
    )

    for i, (uid, stats) in enumerate(sorted_players, start=1):
        player_name = stats.get("username", uid)
        rank = ["👑", "🥈", "🥉"][i - 1] if i <= 3 else str(i)
        row = f"| {rank} | @{player_name} | {stats['total_hits']} | {stats['games_won']} | {stats['games_played']} | {stats.get('best_streak', 0)} | {stats['ships_sunk']} |\n"
        rows += row

    return header + divider + rows

with open("README.md", "r") as f:
    readme = f.read()

# Update all sections
start = readme.find("<!-- BOARD_START -->")
end = readme.find("<!-- BOARD_END -->") + len("<!-- BOARD_END -->")
readme = readme[:start] + "<!-- BOARD_START -->\n" + render_board_reset() + readme[end - len("<!-- BOARD_END -->"):]

ship_start = readme.find("<!-- SHIP_STATUS_START -->")
ship_end = readme.find("<!-- SHIP_STATUS_END -->") + len("<!-- SHIP_STATUS_END -->")
if ship_start != -1:
    readme = readme[:ship_start] + "<!-- SHIP_STATUS_START -->\n" + render_ship_status_reset() + readme[ship_end - len("<!-- SHIP_STATUS_END -->"):]

stats_start = readme.find("<!-- GAME_STATS_START -->")
stats_end = readme.find("<!-- GAME_STATS_END -->") + len("<!-- GAME_STATS_END -->")
if stats_start != -1:
    readme = readme[:stats_start] + "<!-- GAME_STATS_START -->\n" + render_game_stats_reset() + readme[stats_end - len("<!-- GAME_STATS_END -->"):]

hist_start = readme.find("<!-- HISTORY_MOVES_START -->")
hist_end = readme.find("<!-- HISTORY_MOVES_END -->") + len("<!-- HISTORY_MOVES_END -->")
if hist_start != -1:
    readme = readme[:hist_start] + "<!-- HISTORY_MOVES_START -->\n" + render_move_history_reset() + readme[hist_end - len("<!-- HISTORY_MOVES_END -->"):]

lb_start = readme.find("<!-- LEADERBOARD_START -->")
lb_end = readme.find("<!-- LEADERBOARD_END -->") + len("<!-- LEADERBOARD_END -->")
readme = readme[:lb_start] + "<!-- LEADERBOARD_START -->\n" + render_leaderboard_reset() + readme[lb_end - len("<!-- LEADERBOARD_END -->"):]

at_start = readme.find("<!-- ALL_TIME_START -->")
at_end = readme.find("<!-- ALL_TIME_END -->") + len("<!-- ALL_TIME_END -->")
if at_start != -1:
    readme = readme[:at_start] + "<!-- ALL_TIME_START -->\n" + render_all_time_leaderboard(all_time_lb) + readme[at_end - len("<!-- ALL_TIME_END -->"):]

with open("README.md", "w") as f:
    f.write(readme)

# GitHub comment and close
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("GITHUB_REPOSITORY")
ISSUE_NUMBER = int(os.getenv("ISSUE_NUMBER"))
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)
issue = repo.get_issue(number=ISSUE_NUMBER)

victory_msg = f"🎉 **Congratulations @{winner_name}!** 🏆\n\n" if winner_name else ""
issue.create_comment(
    f"{victory_msg}🔄 **Game Reset Complete!**\n\n"
    f"✅ Ships repositioned\n"
    f"✅ Board cleared\n"
    f"✅ Current game leaderboard reset\n"
    f"✅ Round archived as `round_{next_num:03}.json`\n"
    f"✅ All-time stats preserved\n\n"
    f"Ready for the next battle! 🚢"
)

time.sleep(30)
issue.edit(state="closed")
