import json

def load_game_state():
    """Load Connect Four game state"""
    try:
        with open('game_state.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            'board': [['·' for _ in range(7)] for _ in range(6)],
            'current_player': 'Red',
            'game_over': False,
            'winner': None,
            'move_count': 0,
            'history': []
        }

def load_stats():
    """Load game statistics"""
    try:
        with open('stats.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            'total_moves': 0,
            'completed_games': 0,
            'total_players': []
        }

def generate_board_markdown(board):
    """Generate the Connect Four board in Markdown table format"""
    lines = []
    
    # Header row with column numbers
    header = "|"
    for col in range(1, 8):
        header += f"[{col}](../../issues/new?title={col}&body=Just%20push%20%27Submit%20new%20issue%27%20without%20editing%20the%20title.%20The%20game%20will%20make%20your%20move!)|"
    lines.append(header)
    
    # Separator
    lines.append("|" + ":---:|" * 7)
    
    # Board rows (6 rows)
    for row in board:
        row_str = "|"
        for cell in row:
            if cell == 'Red':
                row_str += "🔴|"
            elif cell == 'Blue':
                row_str += "🔵|"
            else:
                row_str += " |"
        lines.append(row_str)
    
    return "\n".join(lines)

def generate_move_history(history):
    """Generate the recent moves table"""
    if not history:
        return "_No moves yet! Be the first to play._"
    
    lines = []
    lines.append("| Team | Move | Made by |")
    lines.append("|:---:|:---:|:---:|")
    
    # Show last 10 moves, most recent first
    recent = history[-10:]
    for move in reversed(recent):
        team = move['team']
        column = move['column']
        player = move.get('player', 'Anonymous')
        
        # Make player a clickable link if it's a username
        if player != 'Anonymous' and not player.startswith('@'):
            player = f"@{player}"
        
        lines.append(f"| {team} | {column} | {player} |")
    
    return "\n".join(lines)

def update_readme():
    """Generate the main README.md"""
    state = load_game_state()
    stats = load_stats()
    
    board = state['board']
    current_player = state['current_player']
    game_over = state['game_over']
    winner = state['winner']
    history = state['history']
    
    total_moves = stats.get('total_moves', 0)
    completed_games = stats.get('completed_games', 0)
    total_players = len(stats.get('total_players', []))
    
    # Generate board
    board_markdown = generate_board_markdown(board)
    
    # Generate move history
    history_markdown = generate_move_history(history)
    
    # Build the README
    readme = f"""# Hey, I'm Shriya Asija 👋

I'm currently a third-year student studying Computer Science at PES University.

---

## 🎮 Join my community Connect Four game!

![Moves played](https://img.shields.io/badge/Moves_played-{total_moves}-blue)
![Completed games](https://img.shields.io/badge/Completed_games-{completed_games}-brightgreen)
![Total players](https://img.shields.io/badge/Total_players-{total_players}-orange)

Everyone is welcome to participate! To make a move, click on the **column number** you wish to drop your disk in.

"""

    if game_over:
        if winner:
            readme += f"### Game Over! The **{winner}** team wins!\n\n"
        else:
            readme += "### Game Over! It's a draw!\n\n"
        readme += "[Click here to start a new game!](../../issues/new?title=reset&body=Reset%20the%20game)\n\n"
    else:
        readme += f"It is the **{current_player.lower()} team's turn** to play.\n\n"

    readme += board_markdown
    readme += "\n\n"
    
    if not game_over:
        readme += """Tired of waiting? [Request a move](../../issues/new?title=connect4bot&body=@connect4bot%20please%20make%20a%20move) from Connect4Bot 🤖

"""
    
    readme += """Interested in how everything works? [Click here](./HOW_IT_WORKS.md) to read up on what's happening behind the scenes.

---

## ⏰ Most recent moves

"""
    readme += history_markdown
    readme += """

---

## 📊 Game Statistics

- **Total moves played**: {0}
- **Completed games**: {1}
- **Unique players**: {2}

---

## 🛠️ How to Play

1. Click on a **column number (1-7)** above
2. This creates a GitHub issue automatically
3. The game processes your move within seconds
4. Your disk drops to the lowest available spot in that column
5. First team to get **4 in a row** (horizontal, vertical, or diagonal) wins!

### Manual Play
Don't want to use the clickable numbers? Create an issue manually:
- **Make a move**: Create an issue with any number 1-7 in the title (e.g., "move 4" or just "4")
- **Reset game**: Create an issue with "reset" in the title

_This game runs entirely on GitHub Actions • Last updated automatically with each move_
""".format(total_moves, completed_games, total_players)
    
    # Write to README.md
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme)
    
    print("README.md updated successfully!")

if __name__ == '__main__':
    update_readme()