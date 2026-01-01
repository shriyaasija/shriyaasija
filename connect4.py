import json
import sys

class ConnectFour:
    def __init__(self):
        self.state_file = 'connect4_state.json'
        self.rows = 6
        self.cols = 7
        self.load_state()

    def load_state(self):
        """Load game state from JSON file"""
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
                self.board = state['board']
                self.current_player = state['current_player']
                self.game_over = state['game_over']
                self.winner = state['winner']
                self.move_count = state['move_count']
                self.history = state.get('history', [])
        except FileNotFoundError:
            self.reset_game()

    def save_state(self):
        """Save game state to JSON file"""
        state = {
            'board': self.board,
            'current_player': self.current_player,
            'game_over': self.game_over,
            'winner': self.winner,
            'move_count': self.move_count,
            'history': self.history
        }
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

    def reset_game(self):
        """Reset game to initial state"""
        self.board = [['.' for _ in range(self.cols)] for _ in range(self.rows)]
        self.current_player = '🔴'
        self.game_over = False
        self.winner = None
        self.move_count = 0
        self.history = []
        self.save_state()

    def get_lowest_empty_row(self, col):
        for row in range(self.rows - 1, -1, -1):
            if self.board[row][col] == '.':
                return row
        return None
    
    def make_move(self, column):
        # validate game state
        if self.game_over:
            return False, "Game is over! Create an issue with 'c4reset' to start a new game."
        
        # validate column 
        if column < 0 or column >= self.cols:
            return False, f"Invalid column {column}. Choose 1-7."
        
        row = self.get_lowest_empty_row(column)
        if row is None:
            return False, f"Column {column + 1} is full! Choose another column."
        
        # place the piece
        self.board[row][column] = self.current_player
        self.move_count += 1

        # track move history
        self.history.append({
            'player': self.current_player,
            'column': column + 1,
            'row': row, 
            'move_number': self.move_count
        })

        self.update_stats()

        # check for winner
        if self.check_winner(row, column):
            self.game_over = True
            self.winner = self.current_player
            self.update_stats(game_completed=True)
            self.save_state()
            return True, f"{self.current_player} wins! Create an issue with 'c4reset' to play again."
        
        # check for draw (full board)
        if self.move_count == self.rows * self.cols:
            self.game_over = True
            self.update_stats(game_completed=True)
            self.save_state()
            return True, "Game ended in a draw! Create an issue with 'c4reset' to play again."
        
        # switch player
        self.current_player = '🟡' if self.current_player == '🔴' else '🔴'
        self.save_state()
        
        return True, f"Move successful! Next player: {self.current_player}"
    
    def check_winner(self, row, col):
        player = self.current_player

        directions = [
            (0, 1), # horizontal
            (1, 0), # vertical
            (1, 1), # diagonal 1
            (1, -1) # diagonal 2
        ]

        for dr, dc in directions:
            count = 1

            # check in positive direction
            count += self.count_consecutive(row, col, dr, dc, player)

            # check in negative direction 
            count += self.count_consecutive(row, col, -dr, -dc, player)

            if count >= 4:
                return True
            
        return False
    
    def count_consecutive(self, row, col, dr, dc, player):
        """
        Count consecutive pieces in a direction starting from (row, col)
        dr = row direction, dc = col direction
        """
        count = 0
        r, c = row + dr, col + dc

        while (0 <= r < self.rows and 
               0 <= c < self.cols and
               self.board[r][c] == player):
            count += 1
            r += dr
            c += dc

        return count 
    
    def update_stats(self, game_completed=False):
        """Update game statistics"""
        try:
            with open('connect4_stats.json', 'r') as f:
                stats = json.load(f)
        except FileNotFoundError:
            stats = {
                'total_moves': 0,
                'completed_games': 0,
                'total_players': []
            }

        stats['total_moves'] = stats.get('total_moves', 0) + 1

        if game_completed:
            stats['completed_games'] = stats.get('completed_games', 0) + 1

        with open('connect4_stats.json', 'w') as f:
            json.dump(stats, f, indent=2)
        
    def get_board_display(self):
        """Generate visual board for README"""
        display = "### Current Game\n\n"
        
        # Column numbers header
        display += "| |"
        for col in range(1, self.cols + 1):
            display += f"{col}|"
        display += "\n"
        
        # Separator
        display += "|" + ":---:|" * (self.cols + 1) + "\n"
        
        # Board rows (top to bottom)
        for row_idx, row in enumerate(self.board):
            display += f"|**{row_idx + 1}**|"
            for cell in row:
                # Show empty cells as spaces for cleaner look
                cell_display = " " if cell == "·" else cell
                display += f"{cell_display}|"
            display += "\n"
        
        display += "\n"
        
        # Game status
        if self.game_over:
            if self.winner:
                display += f"**🎉 {self.winner} wins!**\n\n"
            else:
                display += "**Game ended in a draw!**\n\n"
            display += "Create an issue with title `c4reset` to start a new game.\n\n"
        else:
            display += f"**Current turn:** {self.current_player}\n\n"
            display += "**Make a move:** Create an issue with title like `c4move: 4` (column 1-7)\n\n"
        
        return display
    
def parse_move(title):
    """Parse move from issue title"""
    title = title.lower().strip()

    # handle reset command
    if title in ['c4reset', 'reset connect4', 'reset c4']:
        return 'reset'
    
    if 'c4move' in title:
        move_part = title.split('c4move:')[1].strip()
    elif 'move:' in title:
        move_part = title.split('move:')[1].strip()
    else:
        move_part = title.strip()

    try:
        column = int(move_part)
        if 1 <= column <= 7:
            return column - 1
    except ValueError:
        pass

    return None

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Error: No issue title provided")
        sys.exit(1)

    issue_title = sys.argv[1]
    game = ConnectFour()

    move = parse_move(issue_title)

    if move == 'reset':
        game.reset_game()
        print("Game reset! 🔴 starts.")
    elif move is not None:
        success, message = game.make_move(move)
        print(message)
    else:
        print(f"Invalid move format. Use 'c4move: 4' (column 1-7) or 'c4reset' to restart.")