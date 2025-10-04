# 🚢 GitHub Battleships

Welcome to **GitHub Battleships** — a turn-based game powered entirely by GitHub Issues and Actions!

Sink ships, climb the leaderboard, and flex your strategic genius — all from the comfort of your GitHub account.

---

## How to Play github-battleships?

1. **Open a new issue** with your move in the title: `Move: B4`

*(Only one move per issue, please!)*

2. The bot will:
- Check if your move is valid
- Update the game board
- Reply to your issue with the result: `Hit!`, `Miss!`, or `Already Played`

3. **Check the board** in [`game/board.json`](game/board.json) to see progress.

---

## The Game Rules

- The board is 10x10 (A–J rows, 1–10 columns)
- Ships are hidden — you won't know their locations!
- Hits are marked with `"X"`, misses with `"O"`
- First player to sink all ships wins eternal glory (and maybe a badge 👑)

---

## Leaderboard (coming soon..)

Coming soon in [`game/leaderboard.json`](game/leaderboard.json)!  
Track your hits, misses, and total score.

---

## Powered By

- GitHub Actions
- Python based game logic
- JSON-based board state
- Your brilliant moves ofc!

---

## 💬 Any Questions or Ideas?

Open an issue titled `Suggestion:` or `Question:` and let’s make this game even better.

---

Ready to fire your first shot? 
**Open an issue and type your move now!** 🎯

## 🎯 Current Game Board

|   | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|----|
| A |   |   |   |   |   |   |   |   |   |    |
| B |   |   |   |   |   |   |   |   |   |    |
| C |   |   |   |   |   |   |   |   |   |    |
| D |   |   |   |   |   |   |   |   |   |    |
| E |   |   |   |   |   |   |   |   |   |    |
| F |   |   |   |   |   |   |   |   |   |    |
| G |   |   |   |   |   |   |   |   |   |    |
| H |   |   |   |   |   |   |   |   |   |    |
| I |   |   |   |   |   |   |   |   |   |    |
| J |   |   |   |   |   |   |   |   |   |    |


