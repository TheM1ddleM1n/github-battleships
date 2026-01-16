# 🚢 GitHub Battleships

Welcome to **GitHub Battleships** — a turn-based game powered entirely by GitHub Issues and Actions!

Sink ships, climb the leaderboard, and flex your strategic genius — all from the comfort of your own GitHub Account!

---

## How to Play

1. **Open a new issue** with your move in the title: `Move: B4` or `/move B4`

*(Only one move per issue, please! DO NOT SPAM consecutive cells like B4, B5, B6...)*

2. The bot will:
   - Check if your move is valid
   - Update the game board
   - Reply to your issue with the result: `Hit!`, `Miss!`, or `Already Played`
   - Award achievements for milestones

---

## Game Rules

- **Board:** 10x10 (A–J rows, 1–10 columns)
- **Ships:** 5 hidden ships totaling 16 cells
- **Hits:** Marked with `💥` | **Misses:** Marked with `🌊`
- **Victory:** First player to sink all ships wins eternal glory 👑
- **Cooldown:** 2-hour wait between moves (reduced for active players!)
  - After 20 moves: 1.5 hours
  - After 50 moves: 1 hour
  - Owner (@TheM1ddleM1n): No cooldown
- **Strategy:** Mix up your moves! Systematic patterns are detected 🎲
- **Achievements:** Unlock badges by hitting milestones
- **No Cheating:** Play fair or this experiment ends! 🤐

---

## 🎯 Current Game Board

<!-- BOARD_START -->
|   | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| A | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 🌊 |
| B | ⬜ | 🌊 | ⬜ | ⬜ | 💥 | 💥 | 💥 | 💥 | 💥 | 🌊 |
| C | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| D | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| E | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| F | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 💥 | ⬜ | ⬜ | ⬜ |
| G | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| H | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| I | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| J | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
<!-- BOARD_END -->

---

<!-- SHIP_STATUS_START -->
### 🚢 Fleet Status

- 🛳️ **CARRIER** (5 cells): 💀 **SUNK**
- ⚓ **BATTLESHIP** (4 cells): 🔥 **1/4** damaged
- 🔱 **SUBMARINE** (3 cells): ✅ Afloat
- ⛴️ **DESTROYER** (2 cells): ✅ Afloat
- 🛥️ **PATROL** (2 cells): ✅ Afloat
<!-- SHIP_STATUS_END -->

---

<!-- GAME_STATS_START -->
### 📊 Game Statistics

- 🎯 **Ship Cells Remaining:** 10/16
- 🎲 **Total Moves:** 9
- 💥 **Total Hits:** 6
- 🌊 **Total Misses:** 3
- 📈 **Community Accuracy:** 66.7%
- 👥 **Active Players:** 1
<!-- GAME_STATS_END -->

---

<!-- HISTORY_MOVES_START -->
### 📜 Recent Moves

- 💥 @TheM1ddleM1n: `F7` - Hit (battleship)
- 💥 @TheM1ddleM1n: `B9` - Hit (carrier)
- 💥 @TheM1ddleM1n: `B8` - Hit (carrier)
- 💥 @TheM1ddleM1n: `B7` - Hit (carrier)
- 💥 @TheM1ddleM1n: `B6` - Hit (carrier)
- 💥 @TheM1ddleM1n: `B5` - Hit (carrier)
- 🌊 @TheM1ddleM1n: `B10` - Miss
- 🌊 @TheM1ddleM1n: `B2` - Miss
- 🌊 @TheM1ddleM1n: `A10` - Miss
<!-- HISTORY_MOVES_END -->

---

## 🏅 Current Game Leaderboard

<!-- LEADERBOARD_START -->
| Rank | Player | 🖼️ Avatar | 🏹 Hits | 💦 Misses | 🎯 Accuracy | 🔥 Streak | 🚢 Sunk |
|------|--------|-----------|----------|------------|--------------|------------|----------|
| 🥇 | @TheM1ddleM1n 🔥 Hot Streak 🚢 Ship Sinker | <img src='https://github.com/TheM1ddleM1n.png' width='32' height='32'> | 6 | 3 | 0.67 | 6 | 1 |
<!-- LEADERBOARD_END -->

---

## 👑 All-Time Leaderboard

<!-- ALL_TIME_START -->
| Rank | Player | 🏹 Total Hits | 🏆 Wins | 🎮 Games | 🔥 Best Streak | 🚢 Ships Sunk |
|------|--------|---------------|---------|----------|----------------|----------------|
| 👑 | @TheM1ddleM1n | 8 | 0 | 0 | 6 | 1 |
<!-- ALL_TIME_END -->

---

## 🏆 Achievements

***Unlock badges by hitting milestones***

- 🎯 **Sharpshooter** - 80%+ accuracy with 10+ moves
- 🔥 **Hot Streak** - 5 consecutive hits in a row
- ⚡ **First Blood** - Get the first hit of the game
- 🚢 **Ship Sinker** - Sink your first ship in a game
- 💀 **Fleet Destroyer** - Sink 3 or more ships in a game
- 🏆 **Victory Royale** - Win a game

---

## 🛳️ Fleet Details

| Ship | Size | Icon | Status |
|------|------|------|--------|
| Carrier | 5 cells | 🛳️ | Longest ship |
| Battleship | 4 cells | ⚓ | Classic warship |
| Submarine | 3 cells | 🔱 | Stealthy |
| Destroyer | 2 cells | ⛴️ | Fast attack |
| Patrol | 2 cells | 🛥️ | Reconnaissance |

---

## 🎮 Example Moves

Here are some ways to make your move:

```
✅ Valid moves:
- /move A1
- /move J10
- Move: B5
- move c3 (lowercase works too!)

❌ Invalid moves:
- B11 (out of bounds)
- 1A (wrong format)
- Move B4 B5 B6 (multiple cells)
```

---

## 💡 Tips for Success

1. **Mix it up** - Don't scan rows/columns systematically. You'll get warned! 🎲
2. **Be patient** - Respect the cooldown. Active players get reduced wait times ⏰
3. **Track patterns** - Notice where ships are likely to be (corners, middle)
4. **Hunt efficiently** - Once you hit a ship, search nearby cells
5. **Play fair** - No cheating or this experiment ends 🤐

---

## 🔄 Game Commands

### For Players

**Make a move:**
```
Title: Move: B4
or
Body: /move J10
```

### For Admins/Collaborators

**Reset the game manually:**
```
Title: Reset Game
```

This command is available only to repo admins. It will:
- Generate new ship positions
- Clear the board
- Reset current game leaderboard
- Preserve all-time stats
- Update the README

---

## 🚀 How It Works

The game runs on **GitHub Actions** with pure Python:

- **GitHub Issues** - Your moves
- **GitHub Actions** - Game logic & state updates
- **JSON files** - Board, ships, leaderboard storage
- **README** - Live game display

Every move:
1. Creates an issue with `/move B4`
2. Bot validates the move
3. Updates board & leaderboard
4. Commits changes to repo
5. Closes the issue

---

## 📊 Statistics

**Game Status:**
- Total rounds played: *Check the `/rounds/` folder*
- Current active players: See leaderboard above
- Longest win streak: See all-time leaderboard
- Most accurate player: See leaderboard accuracy

**Server Performance:**
- Move processing: ~1-2 seconds
- Cooldown: 2 hours (configurable per activity level)
- Board update: Real-time
- Concurrency: Safe (file-locked)

---

## 🔐 Security & Fair Play

- **Anti-Cheat:** Pattern detection alerts on suspicious strategies
- **File Integrity:** Board state is verified before/after moves
- **No Spoilers:** Ship positions are randomized and never revealed until game end
- **Fair Cooldown:** Owner has no cooldown for testing; all other players equal
- **Move Validation:** Every move is checked for validity and conflicts

---

## 🐛 Issues & Suggestions

Found a bug? Have an idea? Open an issue!

**Issue types:**
- 🐛 `Bug: [description]` - Report problems
- 💡 `Suggestion: [description]` - Feature requests
- ❓ `Question: [description]` - Ask questions
- 🎮 `Feedback: [description]` - Game balance feedback

---

## 📖 More Information

For detailed technical documentation, game architecture, and troubleshooting, see:
- **[IMPROVEMENTS.md](./docs/IMPROVEMENTS.md)** - Technical architecture & improvements
- **[SETUP.md](./docs/SETUP.md)** - Installation & configuration guide

---

## 🎯 Quick Start

1. **Read the rules** (above)
2. **Look at the board** (current game board section)
3. **Pick a cell** (A1 to J10)
4. **Open an issue** with title: `Move: B4`
5. **Wait for the bot** to respond with hit/miss
6. **Climb the leaderboard!** 🏆

---

## 💬 FAQ

**Q: How long do I have to wait between moves?**
A: 2 hours normally, but it reduces to 1.5 hours after 20 moves, and 1 hour after 50 moves. Owner has no cooldown.

**Q: Can I see where the ships are?**
A: No! Ship positions are secret until the game ends. When someone wins, all ships are revealed.

**Q: What if I accidentally make a move?**
A: You can't undo moves. They're permanent! Double-check before submitting.

**Q: Can multiple people play at once?**
A: Yes! Everyone attacks the same board. First to sink all ships wins.

**Q: How do achievements work?**
A: They unlock automatically when you hit milestones. Check the current game leaderboard to see your badges!

**Q: Is there a maximum number of moves?**
A: No! The game goes until someone sinks all ships.

**Q: Why did I get a pattern warning?**
A: The game detects systematic grid-sweeping and gently suggests mixing up your strategy. It's just a warning—keep playing your way!

---

## Powered By

- ⚙️ **GitHub Actions** - Workflow automation
- 🐍 **Python** - Game logic
- 📄 **JSON** - State management
- 🔒 **File Locking** - Concurrency safety
- 💾 **Git** - Version control

---

## 🎉 Ready to Play?

**[Create an issue and make your first move now!](../../issues/new?title=Move:%20B4)**

Good luck, Admiral! ⚓🎯

---

**Version:** 2.0 (Improved & Hardened)  
**Last Updated:** January 2026  
**Status:** ✅ Live & Production Ready
