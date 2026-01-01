from connect4 import ConnectFour
import json

def load_stats():
    """Load connect 4 statistics"""
    try: 
        with open('connect4_stats.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            'total_moves': 0,
            'completed_games': 0,
            'total_players': []
        }
    
def update_readme():
    game = ConnectFour()
    stats = load_stats()

    total_players = len(stats.get('total_players', []))

    board_display = "| |"
    for col in range(1, game.cols + 1):
        board_display += f"{col}|"
    board_display += "\n|" + ":---:|" * (game.cols + 1) + "\n"
    
    # Board rows
    for row in game.board:
        board_display += "| |"
        for cell in row:
            cell_display = " " if cell == "·" else cell
            board_display += f"{cell_display}|"
        board_display += "\n"
    
    readme_content = f"""# Hey, I'm Shriya Asija

I'm currently a third-year student at PES University, Bangalore. 

---

## Interactive Connect Four Game!

![Moves played](https://img.shields.io/badge/Moves_played-{stats.get('total_moves', 0)}-blue)
![Completed games](https://img.shields.io/badge/Completed_games-{stats.get('completed_games', 0)}-brightgreen)
![Total players](https://img.shields.io/badge/Total_players-{total_players}-orange)

Everyone is welcome to participate! To make a move, click on the **column number** you wish to drop your disc in.

It is the **{game.current_player} player's turn** to play.

{board_display}

"""
    if game.game_over:
        if game.winner:
            readme_content += f"### 🎉 Game Over! **{game.winner} wins!**\n\n"
        else:
            readme_content += "### Game Over! **It's a draw!**\n\n"
        readme_content += "[Start a new game](../../issues/new?title=c4reset&body=Reset%20the%20Connect%20Four%20board) 🔄\n\n"
    else:
        readme_content += "Waiting for your move! Pick a column above ⬆️\n\n"
    
    readme_content += """---

### 📋 How to Play

1. **Choose a column** (1-7) by creating an issue
2. **Your disc drops to the bottom** of that column (gravity!)
3. **First to get 4 in a row wins!** (horizontal ↔️, vertical ↕️, or diagonal ↗️)
4. Players alternate: 🔴 Red goes first, then 🟡 Yellow

### 🎯 Make Your Move

Click a column to drop your disc:

"""

    # Generate clickable column links
    if not game.game_over:
        move_links = []
        for col in range(1, game.cols + 1):
            # Check if column has space
            if game.get_lowest_empty_row(col - 1) is not None:
                move_links.append(f"[**Column {col}**](../../issues/new?title=c4move:%20{col}&body=Dropping%20disc%20in%20column%20{col})")
            else:
                move_links.append(f"~~Column {col}~~ (Full)")
        
        readme_content += " | ".join(move_links) + "\n\n"
    else:
        readme_content += "_Game is over! Reset to play again._\n\n"
    
    readme_content += """---

### ⏰ Most Recent Moves

"""

    # Show move history
    if game.history:
        readme_content += "| Player | Column | Move # |\n"
        readme_content += "|:---:|:---:|:---:|\n"
        
        recent_moves = game.history[-10:]  # Last 10 moves
        for move in reversed(recent_moves):
            readme_content += f"| {move['player']} | {move['column']} | {move['move_number']} |\n"
    else:
        readme_content += "_No moves yet! Be the first to play._\n"
    
    with open('CONNECT4.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("CONNECT4.md created successfully!")

if __name__ == '__main__':
    update_readme()