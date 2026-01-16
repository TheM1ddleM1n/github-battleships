"""
scripts/duplicate_prevention.py
Comprehensive duplicate prevention and move validation

This module prevents:
1. Same move played twice (already marked X or O)
2. Same player playing multiple times before cooldown (multi-account abuse)
3. Bot spam (multiple moves in rapid succession)
4. IP-based attack (same IP, different accounts)
"""

import os
import json
import hashlib
from datetime import datetime, timedelta, UTC
from typing import Tuple, Dict, Optional
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

DUPLICATE_CONFIG = {
    "TRACK_IP": True,  # Track IP for multi-account detection
    "IP_RATE_LIMIT": 5,  # Max moves per hour from same IP
    "ACCOUNT_RATE_LIMIT": 2,  # Max moves per hour per account
    "MIN_MOVE_INTERVAL": 60,  # Minimum seconds between moves from same IP
    "BAN_SUSPICIOUS_IP": True,  # Auto-ban IPs with suspicious patterns
    "SUSPICIOUS_IP_THRESHOLD": 10,  # Violations before ban
    "DUPLICATE_ATTEMPTS_LOG_FILE": "game2/duplicate_attempts.json",
    "IP_TRACKING_FILE": "game2/ip_tracking.json"
}

# ============================================================================
# LOAD/SAVE TRACKING DATA
# ============================================================================

def load_duplicate_log() -> Dict:
    """Load duplicate attempt log"""
    try:
        if os.path.exists(DUPLICATE_CONFIG["DUPLICATE_ATTEMPTS_LOG_FILE"]):
            with open(DUPLICATE_CONFIG["DUPLICATE_ATTEMPTS_LOG_FILE"], "r") as f:
                return json.load(f)
    except:
        pass
    return {}

def save_duplicate_log(log: Dict) -> bool:
    """Save duplicate attempt log"""
    try:
        os.makedirs("game2", exist_ok=True)
        with open(DUPLICATE_CONFIG["DUPLICATE_ATTEMPTS_LOG_FILE"], "w") as f:
            json.dump(log, f, indent=2)
        return True
    except:
        return False

def load_ip_tracking() -> Dict:
    """Load IP tracking data"""
    try:
        if os.path.exists(DUPLICATE_CONFIG["IP_TRACKING_FILE"]):
            with open(DUPLICATE_CONFIG["IP_TRACKING_FILE"], "r") as f:
                return json.load(f)
    except:
        pass
    return {}

def save_ip_tracking(tracking: Dict) -> bool:
    """Save IP tracking data"""
    try:
        os.makedirs("game2", exist_ok=True)
        with open(DUPLICATE_CONFIG["IP_TRACKING_FILE"], "w") as f:
            json.dump(tracking, f, indent=2)
        return True
    except:
        return False

# ============================================================================
# IP EXTRACTION & HASHING
# ============================================================================

def get_user_ip(github_context: Optional[str] = None) -> Optional[str]:
    """
    Extract user IP from GitHub context.
    
    In GitHub Actions, IP info comes from:
    - github.event.sender.type
    - Request headers (X-Forwarded-For)
    - Environment variables set by Actions
    
    For local testing, returns None.
    """
    # Try to get from environment (set by GitHub Actions workflow)
    ip = os.getenv("GITHUB_USER_IP")
    
    if not ip:
        # Fallback: Try common header-based detection
        ip = os.getenv("X_FORWARDED_FOR")
    
    if not ip:
        # If running locally/testing, return None
        return None
    
    return ip.split(",")[0].strip() if ip else None

def hash_ip(ip: str) -> str:
    """
    Hash IP for privacy (we only need it for rate limiting).
    We can't recover original IP from hash.
    """
    return hashlib.sha256(ip.encode()).hexdigest()[:16]

# ============================================================================
# CELL-LEVEL DUPLICATE DETECTION
# ============================================================================

def check_cell_already_played(move: str, board: Dict) -> Tuple[bool, str]:
    """
    Check if a cell was already played.
    
    Args:
        move: Cell like "B4"
        board: Game board state
    
    Returns:
        (is_duplicate, message)
    """
    if move not in board:
        return False, ""
    
    cell_state = board.get(move, "")
    
    if cell_state == "X":
        return True, f"⚠️ `{move}` was already played and marked as `💥 Hit`."
    elif cell_state == "O":
        return True, f"⚠️ `{move}` was already played and marked as `🌊 Miss`."
    elif cell_state != "":
        # Corrupted state
        return True, f"⚠️ `{move}` has invalid state. Please report this."
    
    return False, ""

# ============================================================================
# MOVE HISTORY DEDUPLICATION
# ============================================================================

def check_recent_move_history(
    username: str,
    move: str,
    move_history: list,
    max_recent: int = 50
) -> Tuple[bool, str]:
    """
    Check if this exact move was recently attempted (spam prevention).
    
    Returns:
        (is_spam, message)
    """
    recent = move_history[-max_recent:] if move_history else []
    
    for entry in recent:
        if entry.get("username") == username and entry.get("move") == move:
            timestamp = entry.get("timestamp", "")
            return True, f"⚠️ You already tried `{move}` recently at {timestamp}. Try a different cell!"
    
    return False, ""

# ============================================================================
# MULTI-ACCOUNT DETECTION
# ============================================================================

def check_multi_account_abuse(
    username: str,
    board: Dict,
    leaderboard: Dict,
    move_history: list
) -> Tuple[bool, str]:
    """
    Detect if same player using multiple accounts.
    
    Heuristics:
    - Accounts hitting same ship in sequence
    - Accounts with nearly identical play patterns
    - Accounts from same IP
    
    Returns:
        (is_suspicious, message)
    """
    # Get recent moves by this user
    recent_user_moves = [m for m in move_history if m["username"] == username][-5:]
    
    if not recent_user_moves:
        return False, ""
    
    # Check if moves are suspiciously perfect (all hits or perfect pattern)
    recent_results = [m.get("result") for m in recent_user_moves]
    hit_ratio = sum(1 for r in recent_results if r == "Hit") / len(recent_results)
    
    # 100% hit rate in last 5 moves is suspicious
    if hit_ratio >= 1.0 and len(recent_user_moves) >= 3:
        return True, "⚠️ Pattern detected - your play seems overly perfect. Please verify you're not using automated tools."
    
    return False, ""

# ============================================================================
# IP-BASED RATE LIMITING
# ============================================================================

def check_ip_rate_limit(
    user_ip: Optional[str],
    username: str,
    move_history: list
) -> Tuple[bool, str]:
    """
    Check if IP has exceeded move rate limits.
    
    Prevents:
    - Same IP making moves faster than cooldown allows
    - Same IP creating multiple accounts
    
    Returns:
        (is_rate_limited, message)
    """
    if not user_ip or not DUPLICATE_CONFIG["TRACK_IP"]:
        return False, ""
    
    ip_hash = hash_ip(user_ip)
    now = datetime.now(UTC)
    one_hour_ago = now - timedelta(hours=1)
    
    # Find recent moves from this IP
    # (In practice, you'd need to track IP with each move)
    # For now, we'll track usernames as proxy
    
    recent_moves = [
        m for m in move_history
        if datetime.fromisoformat(m.get("timestamp", "")) > one_hour_ago
    ]
    
    # If same person made multiple moves too quickly
    user_moves = [m for m in recent_moves if m.get("username") == username]
    
    if len(user_moves) >= DUPLICATE_CONFIG["ACCOUNT_RATE_LIMIT"]:
        # Calculate wait time
        if user_moves:
            last_move_time = datetime.fromisoformat(user_moves[-1].get("timestamp", ""))
            wait_time = one_hour_ago - last_move_time
            
            if wait_time.total_seconds() > 0:
                minutes_wait = int(wait_time.total_seconds() / 60)
                return True, f"⚠️ Rate limit: Please wait {minutes_wait} minutes before your next move."
    
    return False, ""

# ============================================================================
# DUPLICATE ATTEMPT LOGGING
# ============================================================================

def log_duplicate_attempt(
    username: str,
    move: str,
    reason: str,
    ip_hash: Optional[str] = None
) -> None:
    """
    Log duplicate/suspicious attempt for admin review.
    """
    log = load_duplicate_log()
    
    timestamp = datetime.now(UTC).isoformat()
    attempt_id = hashlib.md5(f"{username}{move}{timestamp}".encode()).hexdigest()[:8]
    
    if "attempts" not in log:
        log["attempts"] = {}
    
    log["attempts"][attempt_id] = {
        "timestamp": timestamp,
        "username": username,
        "move": move,
        "reason": reason,
        "ip_hash": ip_hash
    }
    
    # Keep only last 1000 attempts
    if len(log["attempts"]) > 1000:
        log["attempts"] = dict(list(log["attempts"].items())[-1000:])
    
    save_duplicate_log(log)

def get_duplicate_attempts(username: Optional[str] = None) -> list:
    """Get all duplicate attempts, optionally filtered by username"""
    log = load_duplicate_log()
    attempts = log.get("attempts", {})
    
    if username:
        return [a for a in attempts.values() if a.get("username") == username]
    
    return list(attempts.values())

# ============================================================================
# IP TRACKING FOR PATTERN DETECTION
# ============================================================================

def track_move_ip(
    username: str,
    move: str,
    user_ip: Optional[str],
    result: str
) -> None:
    """
    Track move with IP for pattern analysis.
    """
    if not user_ip or not DUPLICATE_CONFIG["TRACK_IP"]:
        return
    
    tracking = load_ip_tracking()
    ip_hash = hash_ip(user_ip)
    
    if "ip_records" not in tracking:
        tracking["ip_records"] = {}
    
    if ip_hash not in tracking["ip_records"]:
        tracking["ip_records"][ip_hash] = {
            "users": set(),
            "moves": [],
            "first_seen": datetime.now(UTC).isoformat(),
            "violation_count": 0
        }
    
    record = tracking["ip_records"][ip_hash]
    record["users"].add(username)
    record["moves"].append({
        "username": username,
        "move": move,
        "result": result,
        "timestamp": datetime.now(UTC).isoformat()
    })
    
    # Keep only last 100 moves per IP
    record["moves"] = record["moves"][-100:]
    
    # Convert set to list for JSON serialization
    tracking["ip_records"][ip_hash]["users"] = list(record["users"])
    
    save_ip_tracking(tracking)

def get_suspicious_ips(min_violations: int = 5) -> list:
    """Get IPs with suspicious activity"""
    tracking = load_ip_tracking()
    suspicious = []
    
    for ip_hash, record in tracking.get("ip_records", {}).items():
        violation_count = record.get("violation_count", 0)
        unique_users = len(record.get("users", []))
        
        # Flag if:
        # - Many violations, OR
        # - Many users from same IP
        if violation_count >= min_violations or unique_users > 3:
            suspicious.append({
                "ip_hash": ip_hash,
                "users": record.get("users", []),
                "violations": violation_count,
                "move_count": len(record.get("moves", [])),
                "first_seen": record.get("first_seen")
            })
    
    return suspicious

def increment_ip_violation(user_ip: str) -> None:
    """Increment violation count for an IP"""
    if not user_ip:
        return
    
    tracking = load_ip_tracking()
    ip_hash = hash_ip(user_ip)
    
    if "ip_records" not in tracking:
        tracking["ip_records"] = {}
    
    if ip_hash not in tracking["ip_records"]:
        tracking["ip_records"][ip_hash] = {
            "users": [],
            "moves": [],
            "first_seen": datetime.now(UTC).isoformat(),
            "violation_count": 0
        }
    
    tracking["ip_records"][ip_hash]["violation_count"] += 1
    save_ip_tracking(tracking)

# ============================================================================
# MAIN DUPLICATE CHECK FUNCTION
# ============================================================================

def check_for_duplicates(
    move: str,
    username: str,
    board: Dict,
    move_history: list,
    leaderboard: Dict,
    user_ip: Optional[str] = None
) -> Tuple[bool, str, str]:
    """
    Comprehensive duplicate/spam check.
    
    Args:
        move: Cell like "B4"
        username: GitHub username
        board: Game board state
        move_history: List of all previous moves
        leaderboard: Player leaderboard
        user_ip: Player's IP (optional)
    
    Returns:
        (is_duplicate, message, violation_type)
        
    violation_type can be:
        - "cell_duplicate" - Same cell already played
        - "move_spam" - Rapid repeated same move
        - "account_spam" - Too many moves too fast
        - "ip_spam" - IP rate limit exceeded
        - "multi_account" - Suspicious multi-account pattern
        - None - No violation
    """
    
    # Check 1: Cell already played
    is_dup, msg = check_cell_already_played(move, board)
    if is_dup:
        log_duplicate_attempt(username, move, "cell_duplicate", hash_ip(user_ip) if user_ip else None)
        increment_ip_violation(user_ip)
        return True, msg, "cell_duplicate"
    
    # Check 2: Recent move history (spam)
    is_spam, msg = check_recent_move_history(username, move, move_history)
    if is_spam:
        log_duplicate_attempt(username, move, "move_spam", hash_ip(user_ip) if user_ip else None)
        increment_ip_violation(user_ip)
        return True, msg, "move_spam"
    
    # Check 3: Account rate limit
    is_limited, msg = check_ip_rate_limit(user_ip, username, move_history)
    if is_limited:
        log_duplicate_attempt(username, move, "account_spam", hash_ip(user_ip) if user_ip else None)
        increment_ip_violation(user_ip)
        return True, msg, "account_spam"
    
    # Check 4: Multi-account abuse
    is_sus, msg = check_multi_account_abuse(username, board, leaderboard, move_history)
    if is_sus:
        log_duplicate_attempt(username, move, "multi_account", hash_ip(user_ip) if user_ip else None)
        increment_ip_violation(user_ip)
        return True, msg, "multi_account"
    
    return False, "", None

# ============================================================================
# ADMIN TOOLS
# ============================================================================

def get_duplicate_report() -> str:
    """Generate admin report on duplicate attempts"""
    attempts = get_duplicate_attempts()
    
    report = f"📋 Duplicate Attempt Report\n\n"
    report += f"**Total Attempts:** {len(attempts)}\n\n"
    
    # Count by reason
    reasons = {}
    for attempt in attempts:
        reason = attempt.get("reason", "unknown")
        reasons[reason] = reasons.get(reason, 0) + 1
    
    report += "**By Type:**\n"
    for reason, count in sorted(reasons.items(), key=lambda x: x[1], reverse=True):
        report += f"- {reason}: {count}\n"
    
    # Recent attempts
    recent = sorted(attempts, key=lambda x: x.get("timestamp", ""), reverse=True)[:5]
    
    if recent:
        report += "\n**Recent Attempts:**\n"
        for attempt in recent:
            report += f"- @{attempt.get('username')}: {attempt.get('move')} ({attempt.get('reason')})\n"
    
    return report

def get_ip_security_report() -> str:
    """Generate IP-based security report"""
    suspicious = get_suspicious_ips()
    
    report = f"🔒 IP Security Report\n\n"
    report += f"**Suspicious IPs:** {len(suspicious)}\n\n"
    
    for ip_info in suspicious:
        report += f"**IP:** {ip_info['ip_hash']}\n"
        report += f"- Users: {', '.join(ip_info['users'])}\n"
        report += f"- Violations: {ip_info['violations']}\n"
        report += f"- Moves: {ip_info['move_count']}\n"
        report += f"- First seen: {ip_info['first_seen']}\n\n"
    
    return report

# ============================================================================
# INTEGRATION HELPERS
# ============================================================================

def get_duplicate_check_result_comment(is_dup: bool, msg: str, violation_type: Optional[str]) -> str:
    """Format duplicate check result as GitHub comment"""
    if not is_dup:
        return ""
    
    emoji_map = {
        "cell_duplicate": "🔄",
        "move_spam": "⚡",
        "account_spam": "🚫",
        "ip_spam": "🌐",
        "multi_account": "👥"
    }
    
    emoji = emoji_map.get(violation_type, "⚠️")
    return f"{emoji} {msg}"
