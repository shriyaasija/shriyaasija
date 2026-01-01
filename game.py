import json
import sys
import os

class TicTacToe:
    def __init__(self):
        """Initialize the game by loading the current state"""
        self.state_file = 'game_state.json'
        self.load_state()
    
    def load_state(self):
        """Load the game state from JSON file"""
        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)
                self.board = state['board']
                self.current_player = state['current_player']
                self.game_over = state['game_over']
                self.winner = state['winner']
                self.move_count = state['move_count']
                self.history = state.get('history', [])
        except FileNotFoundError:
            # If file doesn't exist, create initial state
            self.reset_game()
    
    def save_state(self):
        """Save the current game state to JSON file"""
        state = {
            'board': self.board,
            'current_player': self.current_player,
            'game_over': self.game_over,
            'winner': self.winner,
            'move_count': self.move_count,
            'history': getattr(self, 'history', [])
        }
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def reset_game(self):
        """Reset the game to initial state"""
        self.board = ['·'] * 9
        self.current_player = 'X'
        self.game_over = False
        self.winner = None
        self.move_count = 0
        self.history = []
        self.save_state()
    
    def make_move(self, position):
        """
        Make a move at the given position (0-8)
        Returns: (success, message)
        """
        # Validate the move
        if self.game_over:
            return False, "Game is over! Create an issue with 'reset' to start a new game."
        
        if position < 0 or position > 8:
            return False, f"Invalid position {position}. Use 0-8 or A1-C3."
        
        if self.board[position] != '·':
            return False, f"Position {position} is already taken!"
        
        # Make the move
        self.board[position] = self.current_player
        self.move_count += 1
        
        # Track move history
        if not hasattr(self, 'history'):
            self.history = []
        self.history.append({
            'player': self.current_player,
            'position': position,
            'move_number': self.move_count
        })
        
        # Update stats
        self.update_stats()
        
        # Check for winner
        if self.check_winner():
            self.game_over = True
            self.winner = self.current_player
            self.update_stats(game_completed=True)
            self.save_state()
            return True, f"{self.current_player} wins! Create an issue with 'reset' to play again."
        
        # Check for draw
        if self.move_count == 9:
            self.game_over = True
            self.update_stats(game_completed=True)
            self.save_state()
            return True, "Game ended in a draw! Create an issue with 'reset' to play again."
        
        # Switch player
        self.current_player = 'O' if self.current_player == 'X' else 'X'
        self.save_state()
        
        return True, f"Move successful! Next player: {self.current_player}"
    
    def update_stats(self, game_completed=False):
        """Update game statistics"""
        try:
            with open('stats.json', 'r') as f:
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
        
        with open('stats.json', 'w') as f:
            json.dump(stats, f, indent=2)
    
    def check_winner(self):
        """Check if current player has won"""
        # All possible winning combinations
        winning_combos = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]              # Diagonals
        ]
        
        for combo in winning_combos:
            if (self.board[combo[0]] == self.current_player and
                self.board[combo[1]] == self.current_player and
                self.board[combo[2]] == self.current_player):
                return True
        return False
    
    def get_board_display(self):
        """Generate a visual representation of the board for README"""
        # Create the board with row/column labels
        display = "### Current Game\n\n"
        display += "```\n"
        display += "     A   B   C\n"
        display += "   ┌───┬───┬───┐\n"
        
        for row in range(3):
            display += f" {row + 1} │ "
            for col in range(3):
                pos = row * 3 + col
                display += f"{self.board[pos]} │ "
            display += "\n"
            if row < 2:
                display += "   ├───┼───┼───┤\n"
        
        display += "   └───┴───┴───┘\n"
        display += "```\n\n"
        
        # Add game status
        if self.game_over:
            if self.winner:
                display += f"**{self.winner} wins!**\n\n"
            else:
                display += "**Game ended in a draw!**\n\n"
            display += "Create an issue with title `reset` to start a new game.\n\n"
        else:
            display += f"**Current turn:** {self.current_player}\n\n"
            display += "**Make a move:** Create an issue with title like `move: A1` or `move: B2`\n\n"
        
        return display

def parse_move(title):
    """Parse the move from issue title"""
    title = title.lower().strip()
    
    # Handle reset command
    if title == 'reset':
        return 'reset'
    
    # Handle move commands like "move: A1" or just "A1"
    if 'move:' in title:
        move_part = title.split('move:')[1].strip()
    else:
        move_part = title.strip()
    
    # Convert A1 format to position number
    if len(move_part) == 2:
        col = move_part[0].upper()
        row = move_part[1]
        
        if col in 'ABC' and row in '123':
            col_num = ord(col) - ord('A')
            row_num = int(row) - 1
            position = row_num * 3 + col_num
            return position
    
    # Try direct number format (0-8)
    try:
        position = int(move_part)
        if 0 <= position <= 8:
            return position
    except ValueError:
        pass
    
    return None

if __name__ == '__main__':
    # Get the issue title from command line argument
    if len(sys.argv) < 2:
        print("Error: No issue title provided")
        sys.exit(1)
    
    issue_title = sys.argv[1]
    game = TicTacToe()
    
    # Parse the move
    move = parse_move(issue_title)
    
    if move == 'reset':
        game.reset_game()
        print("Game reset! X starts.")
    elif move is not None:
        success, message = game.make_move(move)
        print(message)
    else:
        print(f"Invalid move format. Use 'move: A1' format or 'reset' to restart.")