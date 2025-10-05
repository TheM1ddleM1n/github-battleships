# 🚢 GitHub Battleships

Welcome to **GitHub Battleships** — a turn-based game powered entirely by GitHub Issues and Actions/Secrets!

Sink ships, climb the leaderboard, and flex your strategic genius — all from the comfort from your own GitHub Account!

---

## How to Play github-battleships?

1. **Open a new issue** with your move in the title: `Move: B4`

*(Only one move per issue, please! 2nd thing THIS IS IMPORTANT - please DO NOT SPAM B4 B5 B6 B7... etc)*

2. The bot will:
- Check if your move is valid
- Update the game board
- Reply to your issue with the result: `Hit!`, `Miss!`, or `Already Played`
- Dual move format support (/move B4 and Move: B4)

---

## The Game Rules

- The board is 10x10 (A–J rows, 1–10 columns)
- Ships are hidden — you won't know their locations!
- Hits are marked with `"X"`, misses with `"O"`
- First player to sink all ships wins eternal glory (and maybe a badge 👑)
- WHEN THE GAME IS COMPLETED please make a issue with the comment `Reset Game`

---

## 🏅 Leaderboard (BROKEN AS OF NOW)

<!-- LEADERBOARD_START -->
| Rank | Player | 🖼️ Avatar | 🏹 Hits | 💦 Misses | 🎯 Accuracy | 🔥 Streak |
|------|--------|-----------|----------|------------|--------------|------------|
| 🥇 | @TheM1ddleM1n | <img src='https://github.com/TheM1ddleM1n.png' width='32' height='32'> | 0 | 1 | 0.0 | 0 |
<!-- LEADERBOARD_END -->


---

## Powered By

- GitHub Actions
- Github Secrets
- Python based game logic
- JSON-based board state
- Your brilliant moves ofc!

---

## 💬 Any Questions, Bugs or Ideas?

Open an issue titled `Suggestion:` or `Question:` and let’s make this game even better!

---

Thanks @DataM0del for opening the first issue! (Bug)

Ready to fire your first shot? 
**Open an issue and type your move now!** 🎯

## 🎯 Current Game Board

<!-- BOARD_START -->
|   | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| A | X | X | X | X | X |   |   |   |   | O |
| B |   |   |   | O |   |   |   |   |   |   |
| C |   |   |   |   |   |   |   |   |   |   |
| D |   |   |   |   |   | O |   |   |   | O |
| E |   |   | X |   |   |   |   |   |   |   |
| F |   |   |   |   |   |   |   |   |   |   |
| G |   |   |   |   |   |   |   |   |   |   |
| H |   |   |   |   | O |   |   |   |   |   |
| I |   |   |   |   |   |   |   |   |   |   |
| J |   |   |   |   |   |   |   |   |   | X |
<!-- BOARD_END -->
