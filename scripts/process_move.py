"""
scripts/process_move.py (UPDATED)
Process player moves with comprehensive duplicate prevention

Integration points with duplicate_prevention.py:
- check_for_duplicates() - Main duplicate check
- log_duplicate_attempt() - Log suspicious activity
- track_move_ip() - Track IP for pattern analysis
"""

import os
import re
import sys
import time
import json
import subprocess
from datetime import datetime, UTC
from github import Github, Auth
from pathlib import Path

# Import shared utilities
sys.path.insert(0, os.path.dirname(__file__))
from common import (
    CONFIG, load_json_safe, save_json_safe, is_valid_move, normalize_move,
    check_cooldown, detect_pattern, get_ship_status, is_game_won,
    get_remaining_ships, check_achievements, render_board, render_ship_status,
    render_move_history, render_game_stats, render_leaderboard,
    render_all_time_leaderboard, update_readme_section, archive_round,
    verify_board_integrity, ensure_directories
)

from duplicate_prevention import (
    check_for_duplicates, get_user_ip, track_move_ip,
    log_duplicate_attempt, get_duplicate_report
)

# ============================================================================
# SETUP
# ============================================================================

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("GITHUB_REPOSITORY")
ISSUE_NUMBER = int(os.getenv("ISSUE_NUMBER"))
GITHUB_ACTOR_ID = os.getenv("GITHUB_ACTOR_ID")

ensure_directories()

try:
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    repo = g.get_repo(REPO_NAME)
    issue = repo.get_issue(number=ISSUE_NUMBER)
    username = issue.user.login
except Exception as e:
    print(f"ERROR: Failed to connect to GitHub: {str(e)}")
    sys.exit(1)

# ============================================================================
# EXTRACT MOVE
# ============================================================================

def extract_move_from_issue() -> str:
    """Extract and validate move from issue title/body"""
    move_pattern = r"(?:/move|Move:)\s*([A-J](?:10|[1-9]))"
    
    title_match = re.search(move_pattern, issue.title, re.IGNORECASE)
    body_match = re.search(move_pattern, issue.body or "", re.IGNORECASE)
    match = title_match or body_match
    
    if not match:
        issue.create_comment("❌ Invalid move format. Use `/move B4` or `Move: B4`.")
        sys.exit(1)
    
    move = normalize_move(match.group(1))
    if not move:
        issue.create_comment(f"❌ `{match.group(1)}` is not a valid cell. Use format like A1, B10, J5")
        sys.exit(1)
    
    return move

# ============================================================================
# LOAD GAME STATE
# ============================================================================

def load_game_state() -> tuple:
    """Load board, ships, and player data with validation"""
    board_path = "game/board.json"
    ships_path = "game/ships.json"
    leaderboard_path = "game2/leaderboard.json"
    all_time_path = "game2/all_time_leaderboard.json"
    move_history_path = "game2/move_history.json"
    achievements_path = "game2/achievements.json"
    
    # Load with locking
    board = load_json_safe(board_path, default={}, use_lock=True)
    ships = load_json_safe(ships_path, default={}, use_lock=True)
    leaderboard = load_json_safe(leaderboard_path, default={}, use_lock=True)
    all_time_lb = load_json_safe(all_time_path, default={}, use_lock=True)
    move_history = load_json_safe(move_history_path, default=[], use_lock=True)
    achievements = load_json_safe(achievements_path, default={}, use_lock=True)
    
    # Validation
    if not board:
        issue.create_comment(
            "❌ ERROR: Board not initialized!\n\n"
            "**To fix:** Create an issue titled `Reset Game`"
        )
        sys.exit(1)
    
    if not ships:
        issue.create_comment(
            "❌ ERROR: Ships not initialized!\n\n"
            "**To fix:** Create an issue titled `Reset Game`"
        )
        sys.exit(1)
    
    # Verify board integrity
    if not verify_board_integrity(board, ships):
        issue.create_comment("⚠️ WARNING: Board state inconsistency detected. Please notify maintainers.")
    
    return board, ships, leaderboard, all_time_lb, move_history, achievements

# ============================================================================
# INITIALIZE PLAYER DATA
# ============================================================================

def init_player_data(leaderboard: dict, all_time_lb: dict, achievements: dict, username: str) -> tuple:
    """Initialize or retrieve player data"""
    user_key = username
    
    player = leaderboard.get(user_key, {
        "hits": 0,
        "misses": 0,
        "streak": 0,
        "username": username,
        "ships_sunk": 0,
        "games_won": 0,
        "games_played": 0,
        "accuracy": 0.0
    })
    
    # Ensure backward compatibility
    for field in ["ships_sunk", "games_won", "games_played", "accuracy", "last_move"]:
        if field not in player:
            player[field] = 0 if field != "accuracy" else 0.0
    
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
    
    return player, all_time_player, user_achievements

# ============================================================================
# DUPLICATE PREVENTION CHECK
# ============================================================================

def validate_move_with_duplicates(
    move: str,
    board: dict,
    leaderboard: dict,
    move_history: list,
    username: str
) -> Tuple[bool, str]:
    """
    Comprehensive move validation including duplicate prevention.
    
    Returns:
        (is_valid, message)
    """
    # Get user IP (if available)
    user_ip = get_user_ip()
    
    # Check for all types of duplicates
    is_duplicate, error_msg, violation_type = check_for_duplicates(
        move=move,
        username=username,
        board=board,
        move_history=move_history,
        leaderboard=leaderboard,
        user_ip=user_ip
    )
    
    if is_duplicate:
        issue.create_comment(error_msg)
        return False, error_msg
    
    return True, ""

# ============================================================================
# PROCESS MOVE
# ============================================================================

def process_move(move: str, board: dict, ships: dict, player: dict, move_history: list) -> dict:
    """
    Process a player move.
    Returns: {
        "is_hit": bool,
        "ship_name": str or None,
        "ship_sunk": bool,
        "result_message": str,
        "is_valid": bool,
        "error": str or None
    }
    """
    result = {
        "is_hit": False,
        "ship_name": None,
        "ship_sunk": False,
        "result_message": "",
        "is_valid": True,
        "error": None
    }
    
    # Check if cell already played (extra safety check)
    if board[move] != "":
        result["is_valid"] = False
        result["error"] = f"⚠️ `{move}` was already played and marked as `{board[move]}`."
        return result
    
    # Check for hit or miss
    is_hit = move in ships
    
    if is_hit:
        board[move] = "X"
        ship_hit = ships[move]
        
        # Check if ship is sunk
        ship_cells = [cell for cell, ship_name in ships.items() if ship_name == ship_hit]
        hit_cells_for_ship = [cell for cell in ship_cells if board.get(cell) == "X"]
        ship_sunk = len(hit_cells_for_ship) == len(ship_cells)
        
        result["is_hit"] = True
        result["ship_name"] = ship_hit
        result["ship_sunk"] = ship_sunk
        
        if ship_sunk:
            result["result_message"] = f"💥🔥 **SUNK!** @{username} destroyed the `{ship_hit.upper()}`! ({len(ship_cells)} cells) 🚢💀"
            player["ships_sunk"] += 1
        else:
            remaining = len(ship_cells) - len(hit_cells_for_ship)
            result["result_message"] = f"💥 **Hit!** @{username} struck the `{ship_hit}`! ({len(hit_cells_for_ship)}/{len(ship_cells)} damaged)"
    else:
        board[move] = "O"
        result["result_message"] = f"🌊 `{move}` is a **Miss** by @{username}."
    
    return result

# ============================================================================
# UPDATE LEADERBOARDS
# ============================================================================

def update_leaderboards(player: dict, all_time_player: dict, is_hit: bool) -> None:
    """Update player statistics"""
    if is_hit:
        player["hits"] += 1
        player["streak"] += 1
        all_time_player["total_hits"] += 1
    else:
        player["misses"] += 1
        player["streak"] = 0
        all_time_player["total_misses"] += 1
    
    # Calculate accuracy
    total = player["hits"] + player["misses"]
    player["accuracy"] = round(player["hits"] / total, 2) if total > 0 else 0.0
    
    # Update best streak
    if player["streak"] > all_time_player.get("best_streak", 0):
        all_time_player["best_streak"] = player["streak"]
    
    # Update timestamp
    player["last_move"] = datetime.now(UTC).isoformat()
    player["username"] = username

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    # Extract move
    move = extract_move_from_issue()
    print(f"Processing move: {move} by @{username}")
    
    # Load game state
    board, ships, leaderboard, all_time_lb, move_history, achievements = load_game_state()
    
    # Initialize player data
    player, all_time_player, user_achievements = init_player_data(
        leaderboard, all_time_lb, achievements, username
    )
    
    # ===== NEW: DUPLICATE PREVENTION CHECK =====
    is_valid, dup_msg = validate_move_with_duplicates(
        move, board, leaderboard, move_history, username
    )
    if not is_valid:
        sys.exit(0)
    # ============================================
    
    # Check cooldown
    is_valid, cooldown_msg = check_cooldown(player, username)
    if not is_valid:
        issue.create_comment(f"🛑 @{username}, slow down! {cooldown_msg} ⏰")
        sys.exit(0)
    
    # Check for suspicious patterns
    is_suspicious, pattern_msg = detect_pattern(move_history, username)
    if is_suspicious:
        issue.create_comment(pattern_msg)
    
    # Validate move
    if move not in board:
        issue.create_comment(f"❌ `{move}` is not a valid cell.")
        sys.exit(1)
    
    # Process the move
    move_result = process_move(move, board, ships, player, move_history)
    
    if not move_result["is_valid"]:
        issue.create_comment(move_result["error"])
        sys.exit(0)
    
    # Update leaderboards
    update_leaderboards(player, all_time_player, move_result["is_hit"])
    
    # Record move in history
    now = datetime.now(UTC)
    move_history.append({
        "username": username,
        "move": move,
        "result": "Hit" if move_result["is_hit"] else "Miss",
        "ship": move_result["ship_name"],
        "timestamp": now.isoformat()
    })
    move_history = move_history[-CONFIG["MOVE_HISTORY_LIMIT"]:]
    
    # ===== NEW: TRACK MOVE FOR IP ANALYSIS =====
    user_ip = get_user_ip()
    track_move_ip(username, move, user_ip, "Hit" if move_result["is_hit"] else "Miss")
    # ===========================================
    
    # Check for achievements
    new_badges = check_achievements(
        player, get_ship_status(ships, board),
        game_won=False,
        existing_badges=user_achievements["badges"]
    )
    
    # Check for game victory
    game_won = is_game_won(ships, board)
    
    if game_won:
        player["games_won"] += 1
        all_time_player["games_won"] += 1
        
        if "🏆 Victory Royale" not in user_achievements["badges"]:
            new_badges.append("🏆 Victory Royale")
            user_achievements["badges"].append("🏆 Victory Royale")
    
    user_achievements["badges"].extend(new_badges)
    
    # Save all data with locking
    save_json_safe("game/board.json", board, use_lock=True)
    save_json_safe("game2/leaderboard.json", leaderboard, use_lock=True)
    save_json_safe("game2/all_time_leaderboard.json", all_time_lb, use_lock=True)
    save_json_safe("game2/move_history.json", move_history, use_lock=True)
    save_json_safe("game2/achievements.json", achievements, use_lock=True)
    
    leaderboard[username] = player
    all_time_lb[username] = all_time_player
    achievements[username] = user_achievements
    
    # Build comment
    achievement_text = ""
    if new_badges:
        achievement_text = f"\n\n🏅 **New Achievements:** {', '.join(new_badges)}"
    
    # Game events
    event_text = ""
    remaining = get_remaining_ships(ships, board)
    if remaining <= 3 and remaining > 0:
        event_text = f"\n\n⚠️ **ALERT:** Only **{remaining}** ship cells remaining! Victory is near! 🎯"
    elif player["streak"] >= 3:
        event_text = f"\n\n🔥 **ON FIRE!** @{username} has a **{player['streak']}** hit streak! 🔥"
    
    issue.create_comment(move_result["result_message"] + achievement_text + event_text)
    
    # Update README
    try:
        with open("README.md", "r") as f:
            readme = f.read()
        
        readme = update_readme_section(
            readme, "<!-- BOARD_START -->", "<!-- BOARD_END -->",
            render_board(board)
        )
        readme = update_readme_section(
            readme, "<!-- SHIP_STATUS_START -->", "<!-- SHIP_STATUS_END -->",
            render_ship_status(ships, board)
        )
        readme = update_readme_section(
            readme, "<!-- GAME_STATS_START -->", "<!-- GAME_STATS_END -->",
            render_game_stats(board, ships, leaderboard)
        )
        readme = update_readme_section(
            readme, "<!-- HISTORY_MOVES_START -->", "<!-- HISTORY_MOVES_END -->",
            render_move_history(move_history)
        )
        readme = update_readme_section(
            readme, "<!-- LEADERBOARD_START -->", "<!-- LEADERBOARD_END -->",
            render_leaderboard(leaderboard, achievements)
        )
        readme = update_readme_section(
            readme, "<!-- ALL_TIME_START -->", "<!-- ALL_TIME_END -->",
            render_all_time_leaderboard(all_time_lb)
        )
        
        with open("README.md", "w") as f:
            f.write(readme)
    except Exception as e:
        print(f"WARNING: Failed to update README: {str(e)}")
    
    # Save commit message
    commit_msg = f"{'💥' if move_result['is_hit'] else '🌊'} @{username}: {move}"
    if game_won:
        commit_msg = f"🏆 @{username} won the game!"
    
    with open("commit_message.txt", "w") as f:
        f.write(commit_msg)
    
    # Handle game end
    if game_won:
        issue.create_comment(f"🎉🏆 **GAME OVER!** @{username} has sunk all ships and **WON THE GAME**! 🎊👑")
        
        # Archive round and trigger reset
        round_num = len([f for f in os.listdir("rounds") if f.startswith("round_")]) + 1 if os.path.exists("rounds") else 1
        success, round_file = archive_round(
            round_num, board, ships, leaderboard, move_history, achievements, username
        )
        
        if success:
            print(f"Round archived to {round_file}")
        
        # Trigger automatic reset
        try:
            subprocess.run(["python", "scripts/archive_and_reset.py"], check=False)
        except Exception as e:
            print(f"WARNING: Failed to trigger automatic reset: {str(e)}")
    
    # Close issue after delay
    time.sleep(30)
    issue.edit(state="closed")
    print("Move processed successfully!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        issue.create_comment(f"❌ ERROR: {str(e)}")
        print(f"FATAL ERROR: {str(e)}")
        sys.exit(1)
