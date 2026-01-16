"""
scripts/manual_reset.py
Manual game reset with improved error handling and locking
"""

import os
import sys
import time
import json
from datetime import datetime, UTC
from github import Github, Auth
from pathlib import Path

# Import shared utilities
sys.path.insert(0, os.path.dirname(__file__))
from common import (
    CONFIG, load_json_safe, save_json_safe, generate_ships, init_empty_board,
    render_board, render_ship_status, render_game_stats, render_move_history,
    render_leaderboard, render_all_time_leaderboard, update_readme_section,
    ensure_directories
)

# ============================================================================
# SETUP
# ============================================================================

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("GITHUB_REPOSITORY")
ISSUE_NUMBER = int(os.getenv("ISSUE_NUMBER"))

ensure_directories()

try:
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    repo = g.get_repo(REPO_NAME)
    issue = repo.get_issue(number=ISSUE_NUMBER)
except Exception as e:
    print(f"ERROR: Failed to connect to GitHub: {str(e)}")
    sys.exit(1)

# ============================================================================
# GENERATE NEW SHIPS
# ============================================================================

def generate_new_ships() -> tuple:
    """Generate and validate new ship configuration"""
    ships, error_msg = generate_ships()
    
    if ships is None:
        return None, error_msg
    
    return ships, ""

# ============================================================================
# RESET GAME STATE
# ============================================================================

def reset_game_state(ships: dict) -> bool:
    """Reset board and current game data"""
    try:
        # Reset board
        board = init_empty_board()
        save_json_safe("game/board.json", board, use_lock=True)
        
        # Reset ships
        save_json_safe("game/ships.json", ships, use_lock=True)
        
        # Reset current game leaderboard
        save_json_safe("game2/leaderboard.json", {}, use_lock=True)
        
        # Reset move history
        save_json_safe("game2/move_history.json", [], use_lock=True)
        
        # Preserve all-time leaderboard and achievements
        all_time_lb = load_json_safe("game2/all_time_leaderboard.json", default={})
        achievements = load_json_safe("game2/achievements.json", default={})
        
        save_json_safe("game2/all_time_leaderboard.json", all_time_lb, use_lock=True)
        save_json_safe("game2/achievements.json", achievements, use_lock=True)
        
        return True
    except Exception as e:
        raise Exception(f"Failed to reset game state: {str(e)}")

# ============================================================================
# UPDATE README
# ============================================================================

def update_readme() -> bool:
    """Update README with reset game state"""
    try:
        with open("README.md", "r") as f:
            readme = f.read()
        
        # Load fresh data to render
        board = init_empty_board()
        ships = load_json_safe("game/ships.json", default={})
        all_time_lb = load_json_safe("game2/all_time_leaderboard.json", default={})
        
        # Update all sections
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
            render_game_stats(board, ships, {})
        )
        
        readme = update_readme_section(
            readme, "<!-- HISTORY_MOVES_START -->", "<!-- HISTORY_MOVES_END -->",
            render_move_history([])
        )
        
        readme = update_readme_section(
            readme, "<!-- LEADERBOARD_START -->", "<!-- LEADERBOARD_END -->",
            render_leaderboard({}, {})
        )
        
        readme = update_readme_section(
            readme, "<!-- ALL_TIME_START -->", "<!-- ALL_TIME_END -->",
            render_all_time_leaderboard(all_time_lb)
        )
        
        with open("README.md", "w") as f:
            f.write(readme)
        
        return True
    except Exception as e:
        raise Exception(f"Failed to update README: {str(e)}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("🔄 Starting manual game reset...")
    
    # Step 1: Generate ships
    print("📍 Generating new ship positions...")
    ships, error_msg = generate_new_ships()
    
    if ships is None:
        error_text = (
            f"❌ **Ship Generation Failed**\n\n"
            f"Error: {error_msg}\n\n"
            f"This is a rare error. Please check:\n"
            f"1. Game board size configuration\n"
            f"2. Ship size configuration\n"
            f"3. Try resetting again"
        )
        issue.create_comment(error_text)
        sys.exit(1)
    
    issue.create_comment(f"✅ Generated new ship positions ({len(ships)} cells)")
    
    # Step 2: Reset game state
    print("🔄 Resetting game state...")
    try:
        reset_game_state(ships)
        issue.create_comment("✅ Game state reset (board cleared, leaderboard reset)")
    except Exception as e:
        error_text = (
            f"❌ **Game Reset Failed**\n\n"
            f"Error: {str(e)}\n\n"
            f"Please check file permissions and try again."
        )
        issue.create_comment(error_text)
        sys.exit(1)
    
    # Step 3: Update README
    print("📝 Updating README...")
    try:
        update_readme()
        issue.create_comment("✅ README updated with reset board state")
    except Exception as e:
        error_text = (
            f"⚠️ **README Update Warning**\n\n"
            f"Game was reset but README update failed: {str(e)}\n\n"
            f"Please manually update the README or restart."
        )
        issue.create_comment(error_text)
        sys.exit(1)
    
    # Final summary
    ship_json_str = json.dumps(ships, indent=2)
    
    summary = (
        "🔄 **Manual Game Reset Complete!**\n\n"
        "✅ New ships generated and positioned\n"
        "✅ Board cleared\n"
        "✅ Current game leaderboard reset\n"
        "✅ Move history cleared\n"
        "✅ All-time stats and achievements preserved\n"
        "✅ README updated\n\n"
        "⚠️ **IMPORTANT:** Update the `SHIPS_JSON` secret with:\n\n"
        "```json\n" + ship_json_str + "\n```\n\n"
        "📍 **Steps:**\n"
        "1. Go to Settings → Secrets and variables → Actions\n"
        "2. Update `SHIPS_JSON` with the JSON above\n"
        "3. Game is ready! 🎯"
    )
    
    issue.create_comment(summary)
    
    print("✅ Manual reset completed successfully!")
    print(f"Ship configuration saved to game/ships.json")
    print("Remember to update SHIPS_JSON secret for production security!")
    
    # Close issue after delay
    time.sleep(30)
    issue.edit(state="closed")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        error_msg = f"❌ FATAL ERROR: {str(e)}"
        try:
            issue.create_comment(error_msg)
        except:
            pass
        print(error_msg)
        sys.exit(1)
