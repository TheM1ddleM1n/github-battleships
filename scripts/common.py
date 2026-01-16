"""
scripts/common.py
Shared utilities for GitHub Battleships game
"""

import json
import os
import random
import fcntl
import hashlib
from datetime import datetime, timedelta, UTC
from typing import Dict, List, Tuple, Optional, Set
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG = {
    "BOARD_SIZE": 10,
    "BOARD_ROWS": "ABCDEFGHIJ",
    "BOARD_COLS": list(range(1, 11)),
    "COOLDOWN_HOURS_BASE": 2,
    "COOLDOWN_HOURS_ACTIVE": 1.5,  # After 20 moves
    "COOLDOWN_HOURS_VETERAN": 1,  # After 50 moves
    "PATTERN_DETECTION_THRESHOLD": 5,
    "OWNER_USERNAME": "TheM1ddleM1n",
    "MOVE_HISTORY_LIMIT": 50,
    "SHIPS": {
        "carrier": 5,
        "battleship": 4,
        "submarine": 3,
        "destroyer": 2,
        "patrol": 2
    },
    "SHIP_EMOJIS": {
        "carrier": "🛳️",
        "battleship": "⚓",
        "submarine": "🔱",
        "destroyer": "⛴️",
        "patrol": "🛥️"
    },
    "MAX_SHIP_PLACEMENT_ATTEMPTS": 100,
    "DIRECTORIES": ["game", "game2", "rounds"]
}

# ============================================================================
# FILE OPERATIONS WITH LOCKING
# ============================================================================

def acquire_lock(file_path: str, timeout: int = 30) -> bool:
    """Try to acquire exclusive lock on file"""
    try:
        f = open(file_path, "a+")
        fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except (IOError, OSError):
        return False

def release_lock(file_path: str):
    """Release file lock"""
    try:
        f = open(file_path, "a+")
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        f.close()
    except:
        pass

def load_json_safe(file_path: str, default: any = None, use_lock: bool = False) -> any:
    """Safely load JSON with optional file locking"""
    try:
        if use_lock:
            # Retry logic for lock acquisition
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    with open(file_path, "r") as f:
                        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                        data = json.load(f)
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                        return data
                except (IOError, OSError):
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(0.5)
                    else:
                        raise
        else:
            with open(file_path, "r") as f:
                return json.load(f)
    except FileNotFoundError:
        return default if default is not None else {}
    except json.JSONDecodeError:
        return default if default is not None else {}

def save_json_safe(file_path: str, data: any, use_lock: bool = False) -> bool:
    """Safely save JSON with optional file locking"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        if use_lock:
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    with open(file_path, "w") as f:
                        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                        json.dump(data, f, indent=2)
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                    return True
                except (IOError, OSError):
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(0.5)
                    else:
                        raise
        else:
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)
            return True
    except Exception as e:
        print(f"ERROR: Failed to save {file_path}: {str(e)}")
        return False

# ============================================================================
# VALIDATION
# ============================================================================

def is_valid_move(move: str) -> bool:
    """Validate move format (e.g., 'A1', 'J10')"""
    if not move or len(move) < 2 or len(move) > 3:
        return False
    
    row = move[0].upper()
    col = move[1:]
    
    if row not in CONFIG["BOARD_ROWS"]:
        return False
    
    try:
        col_num = int(col)
        return 1 <= col_num <= CONFIG["BOARD_SIZE"]
    except ValueError:
        return False

def normalize_move(move: str) -> Optional[str]:
    """Normalize move to uppercase and validate"""
    move = move.strip().upper()
    return move if is_valid_move(move) else None

# ============================================================================
# INITIALIZATION
# ============================================================================

def ensure_directories():
    """Create necessary game directories"""
    for directory in CONFIG["DIRECTORIES"]:
        os.makedirs(directory, exist_ok=True)

def init_empty_board() -> Dict[str, str]:
    """Initialize empty 10x10 board"""
    board = {}
    for row in CONFIG["BOARD_ROWS"]:
        for col in CONFIG["BOARD_COLS"]:
            board[f"{row}{col}"] = ""
    return board

# ============================================================================
# SHIP PLACEMENT
# ============================================================================

def place_ship(size: int, occupied: Set[str]) -> Optional[List[str]]:
    """Place a ship of given size without overlapping occupied cells"""
    for _ in range(CONFIG["MAX_SHIP_PLACEMENT_ATTEMPTS"]):
        orientation = random.choice(["H", "V"])
        row = random.choice(CONFIG["BOARD_ROWS"])
        col = random.choice(CONFIG["BOARD_COLS"])
        
        cells = []
        
        if orientation == "H":
            start_col = col
            if start_col + size - 1 > CONFIG["BOARD_SIZE"]:
                continue
            cells = [f"{row}{start_col + i}" for i in range(size)]
        else:
            start_row = CONFIG["BOARD_ROWS"].index(row)
            if start_row + size - 1 > len(CONFIG["BOARD_ROWS"]) - 1:
                continue
            cells = [f"{CONFIG['BOARD_ROWS'][start_row + i]}{col}" for i in range(size)]
        
        if any(cell in occupied for cell in cells):
            continue
        
        return cells
    
    return None

def generate_ships() -> Tuple[Optional[Dict[str, str]], str]:
    """Generate new random ship configuration. Returns (ships_dict, error_msg)"""
    occupied = set()
    ship_map = {}
    
    for ship_name, size in CONFIG["SHIPS"].items():
        cells = place_ship(size, occupied)
        if cells is None:
            error_msg = f"Failed to place {ship_name} (size {size}) after {CONFIG['MAX_SHIP_PLACEMENT_ATTEMPTS']} attempts"
            return None, error_msg
        
        for cell in cells:
            ship_map[cell] = ship_name
            occupied.add(cell)
    
    return ship_map, ""

# ============================================================================
# SECURITY - CHECKSUMS
# ============================================================================

def calculate_board_checksum(board: Dict[str, str]) -> str:
    """Calculate checksum of current board state for tampering detection"""
    board_str = json.dumps(board, sort_keys=True)
    return hashlib.sha256(board_str.encode()).hexdigest()

def verify_board_integrity(board: Dict[str, str], ships: Dict[str, str]) -> bool:
    """Verify board state is consistent with ships"""
    # All cells should be valid
    for cell in board.keys():
        if not is_valid_move(cell):
            return False
    
    # All X marks should correspond to ship locations
    for cell, mark in board.items():
        if mark == "X" and cell not in ships:
            return False
    
    return True

# ============================================================================
# MOVE VALIDATION & HISTORY
# ============================================================================

def check_cooldown(player_data: Dict, username: str, now: datetime = None) -> Tuple[bool, str]:
    """
    Check if player is within cooldown period.
    Returns (is_valid, message)
    """
    if now is None:
        now = datetime.now(UTC)
    
    # Owner has no cooldown
    if username == CONFIG["OWNER_USERNAME"]:
        return True, ""
    
    last_move_str = player_data.get("last_move")
    if not last_move_str:
        return True, ""
    
    # Parse last move timestamp
    try:
        if last_move_str.endswith('Z'):
            last_move_str = last_move_str.replace('Z', '+00:00')
        last_time = datetime.fromisoformat(last_move_str)
        if last_time.tzinfo is None:
            last_time = last_time.replace(tzinfo=UTC)
    except ValueError:
        return True, ""
    
    # Calculate cooldown based on activity level
    total_moves = player_data.get("hits", 0) + player_data.get("misses", 0)
    if total_moves > 50:
        cooldown_hours = CONFIG["COOLDOWN_HOURS_VETERAN"]
    elif total_moves > 20:
        cooldown_hours = CONFIG["COOLDOWN_HOURS_ACTIVE"]
    else:
        cooldown_hours = CONFIG["COOLDOWN_HOURS_BASE"]
    
    cooldown = timedelta(hours=cooldown_hours)
    remaining = cooldown - (now - last_time)
    
    if remaining.total_seconds() > 0:
        hours = int(remaining.total_seconds() // 3600)
        minutes = int((remaining.total_seconds() % 3600) // 60)
        message = f"Cooldown active: {hours}h {minutes}m remaining"
        return False, message
    
    return True, ""

def detect_pattern(move_history: List[Dict], username: str) -> Tuple[bool, str]:
    """
    Detect systematic patterns (anti-cheat).
    Returns (is_suspicious, warning_message)
    """
    recent_moves = [m for m in move_history if m["username"] == username]
    recent_moves = recent_moves[-CONFIG["PATTERN_DETECTION_THRESHOLD"]:]
    
    if len(recent_moves) < CONFIG["PATTERN_DETECTION_THRESHOLD"]:
        return False, ""
    
    moves_list = [m["move"] for m in recent_moves]
    rows = [m[0] for m in moves_list]
    cols = [int(m[1:]) for m in moves_list]
    
    # Check for sequential patterns
    is_sequential_row = all(ord(rows[i]) == ord(rows[i-1]) + 1 for i in range(1, len(rows)))
    is_sequential_col = all(cols[i] == cols[i-1] + 1 for i in range(1, len(cols)))
    is_same_row = len(set(rows)) == 1
    is_same_col = len(set(cols)) == 1
    
    if (is_sequential_row and is_same_col) or (is_sequential_col and is_same_row):
        return True, "⚠️ Pattern detected! Try mixing up your strategy 🎲"
    
    return False, ""

# ============================================================================
# SHIP STATE
# ============================================================================

def get_ship_status(ships: Dict[str, str], board: Dict[str, str]) -> Dict:
    """Get detailed status of each ship"""
    ship_info = {}
    
    for ship_name, size in CONFIG["SHIPS"].items():
        ship_info[ship_name] = {
            "size": size,
            "hits": 0,
            "cells": [],
            "sunk": False
        }
    
    for cell, ship_name in ships.items():
        if ship_name in ship_info:
            ship_info[ship_name]["cells"].append(cell)
            if board.get(cell) == "X":
                ship_info[ship_name]["hits"] += 1
    
    # Mark sunk ships
    for ship_name, info in ship_info.items():
        if info["size"] > 0 and info["hits"] == info["size"]:
            info["sunk"] = True
    
    return ship_info

def get_remaining_ships(ships: Dict[str, str], board: Dict[str, str]) -> int:
    """Get count of remaining ship cells"""
    all_ship_cells = set(ships.keys())
    hit_cells = {cell for cell, mark in board.items() if mark == "X"}
    return len(all_ship_cells) - len(hit_cells)

def is_game_won(ships: Dict[str, str], board: Dict[str, str]) -> bool:
    """Check if all ships are sunk"""
    all_ship_cells = set(ships.keys())
    hit_cells = {cell for cell, mark in board.items() if mark == "X"}
    return bool(all_ship_cells) and all_ship_cells.issubset(hit_cells)

# ============================================================================
# ACHIEVEMENTS
# ============================================================================

ACHIEVEMENTS = {
    "sharpshooter": {
        "emoji": "🎯",
        "name": "Sharpshooter",
        "condition": "80%+ accuracy with 10+ moves"
    },
    "hot_streak": {
        "emoji": "🔥",
        "name": "Hot Streak",
        "condition": "5 hits in a row"
    },
    "first_blood": {
        "emoji": "⚡",
        "name": "First Blood",
        "condition": "Get the first hit of the game"
    },
    "ship_sinker": {
        "emoji": "🚢",
        "name": "Ship Sinker",
        "condition": "Sink your first ship in a game"
    },
    "fleet_destroyer": {
        "emoji": "💀",
        "name": "Fleet Destroyer",
        "condition": "Sink 3 or more ships in a game"
    },
    "victory_royale": {
        "emoji": "🏆",
        "name": "Victory Royale",
        "condition": "Win a game"
    }
}

def check_achievements(
    player: Dict,
    ship_status: Dict,
    game_won: bool,
    existing_badges: List[str]
) -> List[str]:
    """
    Check and return newly unlocked achievements.
    Returns list of new badge strings like "🎯 Sharpshooter"
    """
    new_badges = []
    total_moves = player.get("hits", 0) + player.get("misses", 0)
    
    # Sharpshooter
    if (player.get("accuracy", 0) >= 0.8 and total_moves >= 10 and
        "🎯 Sharpshooter" not in existing_badges):
        new_badges.append("🎯 Sharpshooter")
    
    # Hot Streak
    if (player.get("streak", 0) >= 5 and "🔥 Hot Streak" not in existing_badges):
        new_badges.append("🔥 Hot Streak")
    
    # First Blood (only if first move AND first hit)
    if (player.get("hits", 0) == 1 and player.get("misses", 0) == 0 and
        "⚡ First Blood" not in existing_badges):
        new_badges.append("⚡ First Blood")
    
    # Ship Sinker
    if (player.get("ships_sunk", 0) >= 1 and "🚢 Ship Sinker" not in existing_badges):
        new_badges.append("🚢 Ship Sinker")
    
    # Fleet Destroyer
    if (player.get("ships_sunk", 0) >= 3 and "💀 Fleet Destroyer" not in existing_badges):
        new_badges.append("💀 Fleet Destroyer")
    
    # Victory Royale
    if game_won and "🏆 Victory Royale" not in existing_badges:
        new_badges.append("🏆 Victory Royale")
    
    return new_badges

# ============================================================================
# RENDERING
# ============================================================================

def render_board(board: Dict[str, str]) -> str:
    """Render board as markdown table"""
    header = "|   | " + " | ".join(str(i) for i in range(1, 11)) + " |\n"
    divider = "|---|" + "---|" * 10 + "\n"
    rows = ""
    
    for row in CONFIG["BOARD_ROWS"]:
        cells = []
        for col in CONFIG["BOARD_COLS"]:
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

def render_ship_status(ships: Dict[str, str], board: Dict[str, str]) -> str:
    """Render fleet status"""
    status_text = "### 🚢 Fleet Status\n\n"
    ship_status = get_ship_status(ships, board)
    
    for ship_name in CONFIG["SHIPS"].keys():
        info = ship_status[ship_name]
        emoji = CONFIG["SHIP_EMOJIS"].get(ship_name, "🚢")
        
        if info["sunk"]:
            status = "💀 **SUNK**"
        elif info["hits"] > 0:
            status = f"🔥 **{info['hits']}/{info['size']}** damaged"
        else:
            status = "✅ Afloat"
        
        status_text += f"- {emoji} **{ship_name.upper()}** ({info['size']} cells): {status}\n"
    
    return status_text

def render_move_history(move_history: List[Dict]) -> str:
    """Render recent moves"""
    history_text = "### 📜 Recent Moves\n\n"
    
    if not move_history:
        return history_text + "*No moves yet! Be the first to fire!*\n"
    
    recent = move_history[-10:][::-1]
    
    for entry in recent:
        result_emoji = "💥" if entry["result"] == "Hit" else "🌊"
        ship_info = f" ({entry['ship']})" if entry.get('ship') else ""
        history_text += f"- {result_emoji} @{entry['username']}: `{entry['move']}` - {entry['result']}{ship_info}\n"
    
    return history_text

def render_game_stats(board: Dict[str, str], ships: Dict[str, str], leaderboard: Dict) -> str:
    """Render game statistics"""
    remaining = get_remaining_ships(ships, board)
    total_ship_cells = len(ships)
    
    total_moves = sum(1 for cell in board.values() if cell in ["X", "O"])
    hit_cells = {cell for cell, mark in board.items() if mark == "X"}
    total_hits = len(hit_cells)
    total_misses = total_moves - total_hits
    
    community_accuracy = round(total_hits / total_moves * 100, 1) if total_moves > 0 else 0
    
    stats_text = "### 📊 Game Statistics\n\n"
    stats_text += f"- 🎯 **Ship Cells Remaining:** {remaining}/{total_ship_cells}\n"
    stats_text += f"- 🎲 **Total Moves:** {total_moves}\n"
    stats_text += f"- 💥 **Total Hits:** {total_hits}\n"
    stats_text += f"- 🌊 **Total Misses:** {total_misses}\n"
    stats_text += f"- 📈 **Community Accuracy:** {community_accuracy}%\n"
    stats_text += f"- 👥 **Active Players:** {len(leaderboard)}\n"
    
    return stats_text

def render_leaderboard(leaderboard: Dict, achievements: Dict) -> str:
    """Render current game leaderboard"""
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
        
        player_achievements = achievements.get(uid, {}).get("badges", [])
        badge_display = " ".join(player_achievements[:3]) if player_achievements else ""
        player_display = f"@{player_name} {badge_display}".strip()
        
        row = f"| {rank} | {player_display} | {avatar_md} | {stats['hits']} | {stats['misses']} | {stats['accuracy']} | {stats['streak']} | {stats.get('ships_sunk', 0)} |\n"
        rows += row
    
    return header + divider + (rows if rows else "| - | *No players yet* | - | - | - | - | - | - |\n")

def render_all_time_leaderboard(all_time_lb: Dict) -> str:
    """Render all-time leaderboard"""
    header = "| Rank | Player | 🏹 Total Hits | 🏆 Wins | 🎮 Games | 🔥 Best Streak | 🚢 Ships Sunk |\n"
    divider = "|------|--------|---------------|---------|----------|----------------|----------------|\n"
    rows = ""
    
    if not all_time_lb:
        return header + divider + "| - | *No players yet* | - | - | - | - | - |\n"
    
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

def update_readme_section(readme: str, start_marker: str, end_marker: str, content: str) -> str:
    """Update a specific section of README between markers"""
    start = readme.find(start_marker)
    end = readme.find(end_marker)
    
    if start == -1 or end == -1:
        return readme
    
    end += len(end_marker)
    return readme[:start] + start_marker + "\n" + content + end_marker + readme[end:]

# ============================================================================
# ARCHIVING
# ============================================================================

def archive_round(
    round_num: int,
    board: Dict[str, str],
    ships: Dict[str, str],
    leaderboard: Dict,
    move_history: List[Dict],
    achievements: Dict,
    winner: Optional[str] = None
) -> Tuple[bool, str]:
    """Archive completed round data"""
    try:
        timestamp = datetime.now(UTC).isoformat()
        
        # Reveal ships
        revealed_board = board.copy()
        for coord in ships:
            if revealed_board.get(coord) == "":
                revealed_board[coord] = "🚢"
        
        round_data = {
            "timestamp": timestamp,
            "round_number": round_num,
            "winner": winner,
            "board": board,
            "revealed_board": revealed_board,
            "leaderboard": leaderboard,
            "move_history": move_history,
            "achievements": achievements
        }
        
        os.makedirs("rounds", exist_ok=True)
        round_file = f"rounds/round_{round_num:03d}.json"
        
        return save_json_safe(round_file, round_data, use_lock=True), round_file
    except Exception as e:
        return False, str(e)
