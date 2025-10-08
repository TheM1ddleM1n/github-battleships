import os
import json
import re
import time
import subprocess
from datetime import datetime, timedelta, UTC
from github import Github, Auth
from collections import Counter

# Load environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("GITHUB_REPOSITORY")
ISSUE_NUMBER = int(os.getenv("ISSUE_NUMBER"))
user_id = os.getenv("GITHUB_ACTOR_ID")

# Connect to GitHub using new auth method
auth = Auth.Token(GITHUB_TOKEN)
g = Github(auth=auth)
repo = g.get_repo(REPO_NAME)
issue = repo.get_issue(number=ISSUE_NUMBER)
username = issue.user.login
user_key = username

# Extract move
move_pattern = r"(?:/move|Move:)\s*([A-J](?:10|[1-9]))"
title_match = re.search(move_pattern, issue.title, re.IGNORECASE)
body_match = re.search(move_pattern, issue.body or "", re.IGNORECASE)
match = title_match or body_match
if not match:
    issue.create_comment("❌ Invalid move format. Use `/move B4` or `Move: B4`.")
    exit()

move = match.group(1).upper()

# Create directories if they don't exist
os.makedirs("game", exist_ok=True)
os.makedirs("game2", exist_ok=True)

# Load board and ships from FILES, not secrets
try:
    with open("game/board.json", "r") as f:
        board = json.load(f)
except FileNotFoundError:
    issue.create_comment("❌ ERROR: Board file not found! Please run manual reset first.")
    exit(1)

try:
    with open("game/ships.json", "r") as f:
        ships = json.load(f)
except FileNotFoundError:
    issue.create_comment("❌ ERROR: Ships file not found! Please run manual reset first.")
    exit(1)

# Load leaderboard
leaderboard_path = "game2/leaderboard.json"
all_time_path = "game2/all_time_leaderboard.json"
move_history_path = "game2/move_history.json"
achievements_path = "game2/achievements.json"

if os.path.exists(leaderboard_path):
    with open(leaderboard_path, "r") as f:
        leaderboard = json.load(f)
else:
    leaderboard = {}

if os.path.exists(all_time_path):
    with open(all_time_path, "r") as f:
        all_time_lb = json.load(f)
else:
    all_time_lb = {}

if os.path.exists(move_history_path):
    with open(move_history_path, "r") as f:
        move_history = json.load(f)
else:
    move_history = []

if os.path.exists(achievements_path):
    with open(achievements_path, "r") as f:
        achievements = json.load(f)
else:
    achievements = {}

# Initialize player data
player = leaderboard.get(user_key, {
    "hits": 0,
    "misses": 0,
    "streak": 0,
    "username": username,
    "ships_sunk": 0,
    "games_won": 0,
    "games_played": 0
})

# Ensure all required fields exist (for backward compatibility)
if "ships_sunk" not in player:
    player["ships_sunk"] = 0
if "games_won" not in player:
    player["games_won"] = 0
if "games_played" not in player:
    player["games_played"] = 0

all_time_player = all_time_lb.get(user_key, {
    "username": username,
    "total_hits": 0,
    "total_misses": 0,
    "ships_sunk": 0,
    "games_won": 0,
    "games_played": 0,
    "best_streak": 0
})

user_achievements = achievements.get(user_key, {
    "username": username,
    "badges": []
})

# Pattern detection (Anti-cheat #20)
recent_moves = [m for m in move_history if m["username"] == username][-10:]
if len(recent_moves) >= 5:
    # Check for systematic patterns
    moves_list = [m["move"] for m in recent_moves]
    rows = [m[0] for m in moves_list]
    cols = [int(m[1:]) for m in moves_list]
    
    # Check if moving in strict sequence
    is_sequential_row = all(ord(rows[i]) == ord(rows[i-1]) + 1 for i in range(1, len(rows)))
    is_sequential_col = all(cols[i] == cols[i-1] + 1 for i in range(1, len(cols)))
    is_same_row = len(set(rows)) == 1
    is_same_col = len(set(cols)) == 1
    
    if (is_sequential_row and is_same_col) or (is_sequential_col and is_same_row):
        issue.create_comment("⚠️ **Pattern detected!** Systematic grid searching may be less fun for everyone. Try mixing up your strategy! 🎲")

# Cooldown check (Improved #11)
now = datetime.now(UTC)
last_time_str = player.get("last_move")

cooldown_hours = 2
# Reduce cooldown for active players
if player["hits"] + player["misses"] > 20:
    cooldown_hours = 1.5
if player["hits"] + player["misses"] > 50:
    cooldown_hours = 1

if username != "TheM1ddleM1n" and last_time_str:
    try:
        # Handle both timezone-aware and naive datetimes
        if last_time_str.endswith('Z'):
            last_time_str = last_time_str.replace('Z', '+00:00')
        last_time = datetime.fromisoformat(last_time_str)
        if last_time.tzinfo is None:
            # If naive, assume UTC
            last_time = last_time.replace(tzinfo=UTC)
    except ValueError:
        # Fallback for old format
        last_time = datetime.fromisoformat(last_time_str).replace(tzinfo=UTC)
    
    cooldown = timedelta(hours=cooldown_hours)
    remaining = cooldown - (now - last_time)
    if remaining.total_seconds() > 0:
        hours = int(remaining.total_seconds() // 3600)
        minutes = int((remaining.total_seconds() % 3600) // 60)
        issue.create_comment(f"🛑 Woah @{username}, slow down! You need to wait **{hours}h {minutes}m** before your next move. ⏰")
        exit()

# Validate move
if move not in board:
    issue.create_comment(f"❌ `{move}` is not a valid cell.")
    exit()

if board[move] != "":
    issue.create_comment(f"⚠️ `{move}` was already played and marked as `{board[move]}`.")
    exit()

# Process move
is_hit = move in ships
if is_hit:
    board[move] = "X"
    ship_hit = ships[move]
    
    # Check if ship is sunk
    ship_cells = [cell for cell, ship_name in ships.items() if ship_name == ship_hit]
    hit_cells_for_ship = [cell for cell in ship_cells if board.get(cell) == "X"]
    ship_sunk = len(hit_cells_for_ship) == len(ship_cells)
    
    if ship_sunk:
        result = f"💥🔥 **SUNK!** @{username} destroyed the `{ship_hit.upper()}`! ({len(ship_cells)} cells) 🚢💀"
        player["ships_sunk"] += 1
        all_time_player["ships_sunk"] += 1
    else:
        result = f"💥 **Hit!** @{username} struck the `{ship_hit}`! ({len(hit_cells_for_ship)}/{len(ship_cells)} damaged)"
else:
    board[move] = "O"
    result = f"🌊 `{move}` is a **Miss** by @{username}."

# Update leaderboard
if is_hit:
    player["hits"] += 1
    player["streak"] += 1
    all_time_player["total_hits"] += 1
else:
    player["misses"] += 1
    player["streak"] = 0
    all_time_player["total_misses"] += 1

# Update best streak
if player["streak"] > all_time_player.get("best_streak", 0):
    all_time_player["best_streak"] = player["streak"]

total = player["hits"] + player["misses"]
player["accuracy"] = round(player["hits"] / total, 2) if total else 0.0
player["last_move"] = now.isoformat()
player["username"] = username

# Ensure ships_sunk exists
if "ships_sunk" not in player:
    player["ships_sunk"] = 0

leaderboard[user_key] = player
all_time_lb[user_key] = all_time_player

# Add to move history (#2)
move_history.append({
    "username": username,
    "move": move,
    "result": "Hit" if is_hit else "Miss",
    "ship": ships.get(move, None),
    "timestamp": now.isoformat()
})
# Keep last 50 moves
move_history = move_history[-50:]

# Check achievements (#7)
new_badges = []

if player["accuracy"] >= 0.8 and total >= 10 and "🎯 Sharpshooter" not in user_achievements["badges"]:
    new_badges.append("🎯 Sharpshooter")
    user_achievements["badges"].append("🎯 Sharpshooter")

if player["streak"] >= 5 and "🔥 Hot Streak" not in user_achievements["badges"]:
    new_badges.append("🔥 Hot Streak")
    user_achievements["badges"].append("🔥 Hot Streak")

if player["hits"] == 1 and player["misses"] == 0 and "⚡ First Blood" not in user_achievements["badges"]:
    new_badges.append("⚡ First Blood")
    user_achievements["badges"].append("⚡ First Blood")

if player.get("ships_sunk", 0) >= 1 and "🚢 Ship Sinker" not in user_achievements["badges"]:
    new_badges.append("🚢 Ship Sinker")
    user_achievements["badges"].append("🚢 Ship Sinker")

if player.get("ships_sunk", 0) >= 3 and "💀 Fleet Destroyer" not in user_achievements["badges"]:
    new_badges.append("💀 Fleet Destroyer")
    user_achievements["badges"].append("💀 Fleet Destroyer")

achievements[user_key] = user_achievements

# Save all data INCLUDING BOARD
with open("game/board.json", "w") as f:
    json.dump(board, f, indent=2)
with open(leaderboard_path, "w") as f:
    json.dump(leaderboard, f, indent=2)
with open(all_time_path, "w") as f:
    json.dump(all_time_lb, f, indent=2)
with open(move_history_path, "w") as f:
    json.dump(move_history, f, indent=2)
with open(achievements_path, "w") as f:
    json.dump(achievements, f, indent=2)

# Victory check
def reveal_ships(board, ships):
    for coord in ships:
        if board.get(coord) == "":
            board[coord] = "🚢"

all_ship_cells = set(ships.keys())
hit_cells = {cell for cell, mark in board.items() if mark == "X"}

game_won = False
if all_ship_cells and all_ship_cells.issubset(hit_cells):
    game_won = True
    player["games_won"] += 1
    all_time_player["games_won"] += 1
    
    if "🏆 Victory Royale" not in user_achievements["badges"]:
        new_badges.append("🏆 Victory Royale")
        user_achievements["badges"].append("🏆 Victory Royale")
    
    achievements[user_key] = user_achievements
    with open(achievements_path, "w") as f:
        json.dump(achievements, f, indent=2)
    
    issue.create_comment(f"🎉🏆 **GAME OVER!** @{username} has sunk all ships and **WON THE GAME**! 🎊👑")
    reveal_ships(board, ships)

# Comment result with achievements
achievement_text = ""
if new_badges:
    achievement_text = f"\n\n🏅 **New Achievement(s) Unlocked:** {', '.join(new_badges)}"

# Game events (#19)
event_text = ""
remaining_ships = len(all_ship_cells) - len(hit_cells)
if remaining_ships <= 3 and remaining_ships > 0:
    event_text = f"\n\n⚠️ **ALERT:** Only **{remaining_ships}** ship cells remaining! Victory is near! 🎯"
elif player["streak"] >= 3:
    event_text = f"\n\n🔥 **ON FIRE!** @{username} has a **{player['streak']}** hit streak! 🔥"

issue.create_comment(result + achievement_text + event_text)

# Calculate ship status (#1)
def get_ship_status(ships, board):
    ship_info = {
        "carrier": {"size": 5, "hits": 0, "cells": []},
        "battleship": {"size": 4, "hits": 0, "cells": []},
        "submarine": {"size": 3, "hits": 0, "cells": []},
        "destroyer": {"size": 2, "hits": 0, "cells": []},
        "patrol": {"size": 2, "hits": 0, "cells": []}
    }
    
    for cell, ship_name in ships.items():
        if ship_name in ship_info:
            ship_info[ship_name]["cells"].append(cell)
            if board.get(cell) == "X":
                ship_info[ship_name]["hits"] += 1
    
    return ship_info

# Render board (#8 - improved visuals)
def render_board(board):
    header = "|   | " + " | ".join(str(i) for i in range(1, 11)) + " |\n"
    divider = "|---|" + "---|" * 10 + "\n"
    rows = ""
    for row in "ABCDEFGHIJ":
        cells = []
        for col in range(1, 11):
            cell = board.get(f"{row}{col}", " ")
            if cell == "X":
                cells.append("💥")
            elif cell == "O":
                cells.append("🌊")
            elif cell == "🚢":
                cells.append("🚢")
            else:
                cells.append("⬜")
        rows += f"| {row} | " + " | ".join(cells) + " |\n"
    return header + divider + rows

# Render ship status (#1)
def render_ship_status(ships, board):
    ship_status = get_ship_status(ships, board)
    status_text = "### 🚢 Fleet Status\n\n"
    
    ship_emojis = {
        "carrier": "🛳️",
        "battleship": "⚓",
        "submarine": "🔱",
        "destroyer": "⛴️",
        "patrol": "🛥️"
    }
    
    for ship_name, info in ship_status.items():
        if info["size"] > 0:
            emoji = ship_emojis.get(ship_name, "🚢")
            hits = info["hits"]
            size = info["size"]
            
            if hits == size:
                status = "💀 **SUNK**"
            elif hits > 0:
                status = f"🔥 **{hits}/{size}** damaged"
            else:
                status = "✅ Afloat"
            
            status_text += f"- {emoji} **{ship_name.upper()}** ({size} cells): {status}\n"
    
    return status_text

# Render move history (#2)
def render_move_history(history):
    history_text = "### 📜 Recent Moves\n\n"
    
    if not history:
        return history_text + "*No moves yet! Be the first to fire!*\n"
    
    recent = history[-10:][::-1]  # Last 10, reversed
    
    for entry in recent:
        result_emoji = "💥" if entry["result"] == "Hit" else "🌊"
        ship_info = f" ({entry['ship']})" if entry.get('ship') else ""
        history_text += f"- {result_emoji} @{entry['username']}: `{entry['move']}` - {entry['result']}{ship_info}\n"
    
    return history_text

# Render game stats (#9)
def render_game_stats(board, ships, leaderboard):
    all_ship_cells = set(ships.keys())
    hit_cells = {cell for cell, mark in board.items() if mark == "X"}
    remaining = len(all_ship_cells) - len(hit_cells)
    
    total_moves = sum(1 for cell in board.values() if cell in ["X", "O"])
    total_hits = len(hit_cells)
    community_accuracy = round(total_hits / total_moves * 100, 1) if total_moves > 0 else 0
    
    stats_text = "### 📊 Game Statistics\n\n"
    stats_text += f"- 🎯 **Ship Cells Remaining:** {remaining}/{len(all_ship_cells)}\n"
    stats_text += f"- 🎲 **Total Moves:** {total_moves}\n"
    stats_text += f"- 💥 **Total Hits:** {total_hits}\n"
    stats_text += f"- 🌊 **Total Misses:** {total_moves - total_hits}\n"
    stats_text += f"- 📈 **Community Accuracy:** {community_accuracy}%\n"
    stats_text += f"- 👥 **Active Players:** {len(leaderboard)}\n"
    
    return stats_text

# Render leaderboard (#5 - more stats)
def render_leaderboard(leaderboard):
    header = "| Rank | Player | 🖼️ Avatar | 🏹 Hits | 💦 Misses | 🎯 Accuracy | 🔥 Streak | 🚢 Sunk |\n"
    divider = "|------|--------|-----------|----------|------------|--------------|------------|----------|\n"
    rows = ""

    sorted_players = sorted(
        leaderboard.items(),
        key=lambda x: (x[1]["hits"], x[1]["accuracy"], x[1].get("ships_sunk", 0)),
        reverse=True
    )

    for i, (uid, stats) in enumerate(sorted_players, start=1):
        player_name = stats.get("username", uid)
        rank = ["🥇", "🥈", "🥉"][i - 1] if i <= 3 else str(i)
        avatar_url = f"https://github.com/{player_name}.png"
        avatar_md = f"<img src='{avatar_url}' width='32' height='32'>"
        
        # Get achievements
        player_achievements = achievements.get(uid, {}).get("badges", [])
        badge_display = " ".join(player_achievements[:3]) if player_achievements else ""
        player_display = f"@{player_name} {badge_display}".strip()
        
        row = f"| {rank} | {player_display} | {avatar_md} | {stats['hits']} | {stats['misses']} | {stats['accuracy']} | {stats['streak']} | {stats.get('ships_sunk', 0)} |\n"
        rows += row

    return header + divider + rows

# Render all-time leaderboard (#6)
def render_all_time_leaderboard(all_time_lb):
    header = "| Rank | Player | 🏹 Total Hits | 🏆 Wins | 🎮 Games | 🔥 Best Streak | 🚢 Ships Sunk |\n"
    divider = "|------|--------|---------------|---------|----------|----------------|----------------|\n"
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

# Update README
with open("README.md", "r") as f:
    readme = f.read()

# Update board
start = readme.find("<!-- BOARD_START -->")
end = readme.find("<!-- BOARD_END -->") + len("<!-- BOARD_END -->")
new_board = render_board(board)
readme = readme[:start] + "<!-- BOARD_START -->\n" + new_board + readme[end - len("<!-- BOARD_END -->"):]

# Update ship status
ship_start = readme.find("<!-- SHIP_STATUS_START -->")
ship_end = readme.find("<!-- SHIP_STATUS_END -->") + len("<!-- SHIP_STATUS_END -->")
if ship_start != -1 and ship_end > ship_start:
    new_ship_status = render_ship_status(ships, board)
    readme = readme[:ship_start] + "<!-- SHIP_STATUS_START -->\n" + new_ship_status + readme[ship_end - len("<!-- SHIP_STATUS_END -->"):]

# Update move history
hist_start = readme.find("<!-- HISTORY_MOVES_START -->")
hist_end = readme.find("<!-- HISTORY_MOVES_END -->") + len("<!-- HISTORY_MOVES_END -->")
if hist_start != -1 and hist_end > hist_start:
    new_history = render_move_history(move_history)
    readme = readme[:hist_start] + "<!-- HISTORY_MOVES_START -->\n" + new_history + readme[hist_end - len("<!-- HISTORY_MOVES_END -->"):]

# Update game stats
stats_start = readme.find("<!-- GAME_STATS_START -->")
stats_end = readme.find("<!-- GAME_STATS_END -->") + len("<!-- GAME_STATS_END -->")
if stats_start != -1 and stats_end > stats_start:
    new_stats = render_game_stats(board, ships, leaderboard)
    readme = readme[:stats_start] + "<!-- GAME_STATS_START -->\n" + new_stats + readme[stats_end - len("<!-- GAME_STATS_END -->"):]

# Update current game leaderboard
lb_start = readme.find("<!-- LEADERBOARD_START -->")
lb_end = readme.find("<!-- LEADERBOARD_END -->") + len("<!-- LEADERBOARD_END -->")
new_leaderboard = render_leaderboard(leaderboard)
readme = readme[:lb_start] + "<!-- LEADERBOARD_START -->\n" + new_leaderboard + readme[lb_end - len("<!-- LEADERBOARD_END -->"):]

# Update all-time leaderboard
at_start = readme.find("<!-- ALL_TIME_START -->")
at_end = readme.find("<!-- ALL_TIME_END -->") + len("<!-- ALL_TIME_END -->")
if at_start != -1 and at_end > at_start:
    new_all_time = render_all_time_leaderboard(all_time_lb)
    readme = readme[:at_start] + "<!-- ALL_TIME_START -->\n" + new_all_time + readme[at_end - len("<!-- ALL_TIME_END -->"):]

with open("README.md", "w") as f:
    f.write(readme)

# Save commit message
with open("commit_message.txt", "w") as f:
    if game_won:
        f.write(f"🏆 @{username} won the game!")
    else:
        f.write(f"{'💥' if is_hit else '🌊'} @{username}: {move} - {'Hit' if is_hit else 'Miss'}")

# Auto-close issue
issue.create_comment("🕒 Closing this issue in 30 seconds…")
time.sleep(30)
issue.edit(state="closed")

# Trigger reset if game ended
if game_won:
    subprocess.run(["python", "scripts/archive_and_reset.py"])
