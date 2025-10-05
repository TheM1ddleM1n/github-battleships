# 🚢 GitHub Battleships

Welcome to **GitHub Battleships** — a turn-based game powered entirely by GitHub Issues and Actions/Secrets!

Sink ships, climb the leaderboard, and flex your strategic genius — all from the comfort from your own GitHub Account!

---

## How to Play github-battleships?

1. **Open a new issue** with your move in the title: `Move: B4` or `/move B4`

*(Only one move per issue, please! DO NOT SPAM consecutive cells like B4, B5, B6...)*

2. The bot will:
- Check if your move is valid
- Update the game board
- Reply to your issue with the result: `Hit!`, `Miss!`, or `Already Played`
- Award achievements for milestones
- Track your stats

---

## The Game Rules

- The board is 10x10 (A–J rows, 1–10 columns)
- Ships are hidden — you won't know their locations!
- Hits are marked with `💥`, misses with `🌊`
- First player to sink all ships wins eternal glory 👑
- 2-hour cooldown between moves (reduced for active players!)
- Strategic patterns may be detected - mix up your strategy!

---

## 🎯 Current Game Board

<!-- BOARD_START -->
|   | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| A | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| B | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| C | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| D | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| E | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| F | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| G | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| H | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| I | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| J | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
<!-- BOARD_END -->

---

<!-- SHIP_STATUS_START -->
### 🚢 Fleet Status

- 🛳️ **CARRIER** (5 cells): ✅ Afloat
- ⚓ **BATTLESHIP** (4 cells): ✅ Afloat
- 🔱 **SUBMARINE** (3 cells): ✅ Afloat
- ⛴️ **DESTROYER** (2 cells): ✅ Afloat
- 🛥️ **PATROL** (2 cells): ✅ Afloat
<!-- SHIP_STATUS_END -->

---

<!-- GAME_STATS_START -->
### 📊 Game Statistics

- 🎯 **Ship Cells Remaining:** 16/16
- 🎲 **Total Moves:** 0
- 💥 **Total Hits:** 0
- 🌊 **Total Misses:** 0
- 📈 **Community Accuracy:** 0.0%
- 👥 **Active Players:** 0
<!-- GAME_STATS_END -->

---

<!-- HISTORY_MOVES_START -->
### 📜 Recent Moves

*No moves yet! Be the first to fire!*
<!-- HISTORY_MOVES_END -->

---

## 🏅 Current Game Leaderboard

<!-- LEADERBOARD_START -->
| Rank | Player | 🖼️ Avatar | 🏹 Hits | 💦 Misses | 🎯 Accuracy | 🔥 Streak | 🚢 Sunk |
|------|--------|-----------|----------|------------|--------------|------------|----------|
| - | *No players yet* | - | - | - | - | - | - |
<!-- LEADERBOARD_END -->

---

## 👑 All-Time Leaderboard

<!-- ALL_TIME_START -->
| Rank | Player | 🏹 Total Hits | 🏆 Wins | 🎮 Games | 🔥 Best Streak | 🚢 Ships Sunk |
|------|--------|---------------|---------|----------|----------------|----------------|
| - | *No players yet* | - | - | - | - | - |
<!-- ALL_TIME_END -->

---

## 🏆 Achievements

Unlock badges by hitting milestones!

- 🎯 **Sharpshooter** - 80%+ accuracy with 10+ moves
- 🔥 **Hot Streak** - 5 hits in a row
- ⚡ **First Blood** - Get the first hit of the game
- 🚢 **Ship Sinker** - Sink your first ship
- 💀 **Fleet Destroyer** - Sink 3 or more ships
- 🏆 **Victory Royale** - Win a game

---

## Powered By

- GitHub Actions & Secrets
- Python-based game logic
- JSON-based state management
- Your brilliant moves!

---

## 💬 Any Questions, Bugs or Ideas?

Open an issue titled `Suggestion:` or `Question:` and let's make this game even better!

---

Ready to fire your first shot? 
**Open an issue and type your move now!** 🎯
