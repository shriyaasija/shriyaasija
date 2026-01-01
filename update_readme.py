from game import TicTacToe
import json
import os

def load_stats():
    """Load game statistics"""
    try:
        with open('stats.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            'total_moves': 0,
            'completed_games': 0,
            'total_players': set()
        }

def update_readme():
    """Generate and update the README.md file with current game state"""
    game = TicTacToe()
    stats = load_stats()
    
    # Convert set to count if it exists
    total_players = len(stats.get('total_players', [])) if isinstance(stats.get('total_players'), list) else 0
    
    # Generate the board display
    board_display = "| |1|2|3|\n|:---:|:---:|:---:|:---:|\n"
    
    for row in range(3):
        row_label = chr(65 + row)  # A, B, C
        board_display += f"|**{row_label}**|"
        for col in range(3):
            pos = row * 3 + col
            cell = game.board[pos]
            # Replace · with empty space for cleaner look
            if cell == '·':
                cell = ' '
            board_display += f"{cell}|"
        board_display += "\n"
    
    # Create the full README content
    readme_content = f"""# Hey, I'm Shriya Asija. 
I'm currently a 3rd year student at PES University, Bangalore. Feel free to play a game of Tic Tac Toe with me!

---

## Join my community Tic Tac Toe game!

![Moves played](https://img.shields.io/badge/Moves_played-{stats.get('total_moves', 0)}-blue)
![Completed games](https://img.shields.io/badge/Completed_games-{stats.get('completed_games', 0)}-brightgreen)
![Total players](https://img.shields.io/badge/Total_players-{total_players}-orange)

Everyone is welcome to participate! To make a move, click on the **position** you wish to place your mark in.

It is the **{game.current_player} player's turn** to play.

{board_display}

"""

    # Add game status
    if game.game_over:
        if game.winner:
            readme_content += f"### 🎉 Game Over! **{game.winner} wins!**\n\n"
        else:
            readme_content += f"### Game Over! **It's a draw!**\n\n"
        readme_content += "Want to play again? [Request a reset](../../issues/new?title=reset&body=Reset%20the%20game%20board) to start a new game.\n\n"
    else:
        readme_content += f"Tired of waiting? [Request a move](../../issues/new?title=move:&body=Make%20a%20move) from the Tic Tac Toe Bot 🤖\n\n"
    
    readme_content += """---

### How to Play

1. **Choose a position** by clicking on one of the links below (or create an issue manually)
2. **The game will automatically update** within a few seconds
3. **Wait for your turn** - X and O alternate
4. **First to get 3 in a row wins!** (horizontal, vertical, or diagonal)

### Make Your Move

Click a position to play:

"""

    # Generate clickable move links for empty positions
    move_links = []
    for row in range(3):
        row_label = chr(65 + row)  # A, B, C
        for col in range(3):
            pos = row * 3 + col
            if game.board[pos] == '·' and not game.game_over:
                position = f"{row_label}{col + 1}"
                move_links.append(f"[**{position}**](../../issues/new?title=move:%20{position}&body=Making%20a%20move%20at%20{position})")
    
    if move_links:
        # Display in rows of 3
        for i in range(0, len(move_links), 3):
            readme_content += " | ".join(move_links[i:i+3]) + "\n\n"
    else:
        readme_content += "_No moves available - game is over!_\n\n"
    
    readme_content += """---

### Most Recent Moves

<!-- This will show the last few moves made -->

"""

    # Load move history if it exists
    if hasattr(game, 'history') and game.history:
        readme_content += "| Player | Position | Move # |\n"
        readme_content += "|:---:|:---:|:---:|\n"
        
        # Show last 10 moves
        recent_moves = game.history[-10:]
        for move in reversed(recent_moves):
            row = move['position'] // 3
            col = move['position'] % 3
            position = f"{chr(65 + row)}{col + 1}"
            readme_content += f"| {move['player']} | {position} | {move['move_number']} |\n"
    else:
        readme_content += "_No moves yet! Be the first to play._\n"
    
    readme_content += """

---

### Making a Move Manually

If the clickable links don't work, you can create an issue manually:

1. Go to the [Issues tab](../../issues)
2. Click "New Issue"
3. Title format: `move: A1` (where A-C is row, 1-3 is column)
4. Examples: `move: A1`, `move: B2`, `move: C3`
5. Submit the issue!

To reset the game, create an issue with title: `reset`

_Last updated automatically with each move_
"""
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("README.md updated successfully!")

if __name__ == '__main__':
    update_readme()