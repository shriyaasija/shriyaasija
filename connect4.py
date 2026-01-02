import json
import sys
import os

class ConnectFour:
    def __init__(self):
        """Initialize Connect Four game"""
        self.state_file = 'game_state.json'
        self.stats_file = 'stats.json'
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
        self.board = [['·' for _ in range(self.cols)] for _ in range(self.rows)]
        self.current_player = 'Red'
        self.game_over = False
        self.winner = None
        self.move_count = 0
        self.history = []
        self.save_state()
        print("Game reset! Red team starts.")
    
    def get_lowest_empty_row(self, col):
        """
        Find the lowest empty row in a column 
        Returns row index or None if column is full
        """
        for row in range(self.rows - 1, -1, -1):  # Start from bottom (row 5)
            if self.board[row][col] == '·':
                return row
        return None  # Column is full
    
    def make_move(self, column, player_username=None):
        """
        Drop a piece in the specified column (0-6)
        Returns: (success, message)
        """
        # Validate game state
        if self.game_over:
            return False, "Game is over! Create an issue with title 'reset' to start a new game."
        
        # Validate column
        if column < 0 or column >= self.cols:
            return False, f"Invalid column {column + 1}. Choose 1-7."
        
        # Find where piece will land (gravity!)
        row = self.get_lowest_empty_row(column)
        if row is None:
            return False, f"Column {column + 1} is full! Choose another column."
        
        # Place the piece
        self.board[row][column] = self.current_player
        self.move_count += 1
        
        # Track move history
        move_data = {
            'team': self.current_player,
            'column': column + 1,  # Display as 1-7
            'move_number': self.move_count
        }
        if player_username:
            move_data['player'] = player_username
        
        self.history.append(move_data)
        
        # Update stats
        self.update_stats(player_username)
        
        # Check for winner
        if self.check_winner(row, column):
            self.game_over = True
            self.winner = self.current_player
            self.update_stats(player_username, game_completed=True)
            self.save_state()
            return True, f"{self.current_player} team wins! Create an issue with title 'reset' to play again."
        
        # Check for draw (board full)
        if self.move_count == self.rows * self.cols:
            self.game_over = True
            self.update_stats(player_username, game_completed=True)
            self.save_state()
            return True, "Game ended in a draw! Create an issue with title 'reset' to play again."
        
        # Switch player
        self.current_player = 'Blue' if self.current_player == 'Red' else 'Red'
        self.save_state()
        
        return True, f"Move successful! Next turn: {self.current_player} team"
    
    def check_winner(self, row, col):
        """
        Check if the current player won after placing at (row, col)
        """
        player = self.current_player
        
        # All 4 directions to check
        directions = [
            (0, 1),  
            (1, 0),   
            (1, 1),  
            (1, -1)   
        ]
        
        for dr, dc in directions:
            count = 1  # Count the piece we just placed
            
            # Check in positive direction
            count += self.count_consecutive(row, col, dr, dc, player)
            
            # Check in negative direction
            count += self.count_consecutive(row, col, -dr, -dc, player)
            
            if count >= 4:
                return True
        
        return False
    
    def count_consecutive(self, row, col, dr, dc, player):
        """Count consecutive pieces in a direction"""
        count = 0
        r, c = row + dr, col + dc
        
        while (0 <= r < self.rows and 
               0 <= c < self.cols and 
               self.board[r][c] == player):
            count += 1
            r += dr
            c += dc
        
        return count
    
    def update_stats(self, player_username=None, game_completed=False):
        """Update game statistics"""
        try:
            with open(self.stats_file, 'r') as f:
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
        
        # Track unique players
        if player_username and player_username not in stats.get('total_players', []):
            if 'total_players' not in stats:
                stats['total_players'] = []
            stats['total_players'].append(player_username)
        
        with open(self.stats_file, 'w') as f:
            json.dump(stats, f, indent=2)

def parse_move(title):
    """Parse move from issue title"""
    title = title.lower().strip()
    
    # Handle reset command
    if 'reset' in title:
        return 'reset'
    
    # Extract column number from various formats
    import re
    match = re.search(r'\d+', title)
    if match:
        column = int(match.group())
        if 1 <= column <= 7:
            return column - 1  # Convert to 0-indexed
    
    return None

if __name__ == '__main__':
    # Get issue title and username from command line
    if len(sys.argv) < 2:
        print("Error: No issue title provided")
        sys.exit(1)
    
    issue_title = sys.argv[1]
    player_username = sys.argv[2] if len(sys.argv) > 2 else None
    
    game = ConnectFour()
    
    # Parse the move
    move = parse_move(issue_title)
    
    if move == 'reset':
        game.reset_game()
    elif move is not None:
        success, message = game.make_move(move, player_username)
        print(message)
    else:
        print(f"Invalid move format. Use a column number (1-7) in your issue title, or 'reset' to restart.")