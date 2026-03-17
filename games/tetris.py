import typer
import curses
import random
import time
#Constants
BOARD_WIDTH = 10
BOARD_HEIGHT = 20

PIECES = {
    "I": [
        [(0, 0), (0, 1), (0, 2), (0, 3)],
        [(0, 0), (1, 0), (2, 0), (3, 0)],
    ],
    "O": [
        [(0, 0), (0, 1), (1, 0), (1, 1)],
    ],
    "T": [
        [(0, 0), (0, 1), (0, 2), (1, 1)],
        [(0, 0), (1, 0), (2, 0), (1, 1)],
        [(0, 1), (1, 0), (1, 1), (1, 2)],
        [(0, 0), (1, 0), (2, 0), (1, -1)],
    ],
    "S": [
        [(0, 1), (0, 2), (1, 0), (1, 1)],
        [(0, 0), (1, 0), (1, 1), (2, 1)],
    ],
    "Z": [
        [(0, 0), (0, 1), (1, 1), (1, 2)],
        [(0, 1), (1, 0), (1, 1), (2, 0)],
    ],
    "L": [
        [(0, 0), (0, 1), (0, 2), (1, 0)],
        [(0, 0), (1, 0), (2, 0), (2, 1)],
        [(0, 2), (1, 0), (1, 1), (1, 2)],
        [(0, 0), (0, 1), (1, 1), (2, 1)],
    ],
    "J": [
        [(0, 0), (0, 1), (0, 2), (1, 2)],
        [(0, 0), (0, 1), (1, 0), (2, 0)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 0), (2, 1)],
    ],
}

class Tetris():
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.board = [[0] * BOARD_WIDTH for board_height in range(BOARD_HEIGHT)]
        self.score = 0
        self.game_over = False
        
        self.current_piece = None
        self.current_rotation = 0
        self.piece_x = 0
        self.piece_y = 0
    
    def spawn_piece(self):
        #picks random shape
        self.current_piece = random.choice(list(PIECES.keys()))
        self.current_rotation = 0
        #spawns them top of the board and in the middle
        self.piece_x = BOARD_WIDTH // 2 - 1
        self.piece_y = 0
    
    def draw(self):
            self.stdscr.clear()
            dirty_rectangles = []
            for row, col in enumerate(self.board):
                for col_array, col_item in enumerate(col):
                    if col_item != 0:
                        self.stdscr.addstr(row, col_array, "█")
            #Checks if we have a piece the game is dropping
            if self.current_piece:
                #get the coords for where the pixels should be for the piece
                falling_piece = PIECES[self.current_piece][self.current_rotation]
                for y, x in falling_piece:
                    new_x_position = x + self.piece_x
                    new_y_position = y + self.piece_y
                    #checks if it's within the boards
                    if 0 <= new_y_position < BOARD_HEIGHT and 0 <= new_x_position < BOARD_WIDTH:
                        #This draws the shape
                       self.stdscr.addstr(new_y_position, new_x_position, "█")
            for y in range(BOARD_HEIGHT):
                self.stdscr.addstr(y, BOARD_WIDTH, "|")
            self.stdscr.addstr(BOARD_HEIGHT, 0, "-" * BOARD_WIDTH)
            self.stdscr.refresh() # Push the drawing to the screen
    def check_collision(self, user_input_y, user_input_x):
        #Gets the piece that is falling and its rotation
        falling_piece = PIECES[self.current_piece][self.current_rotation]
        #Gets the x and y coordinates of it and increment by whatever user_input_y and user_input_x is (usually 1)
        for falling_piece_y, falling_piece_x in falling_piece:
            #self.piece_y and self.piece_x will store the new value and keep increasing until it reaches the floor or it collides with the wall
            new_y = self.piece_y + falling_piece_y + user_input_y
            new_x = self.piece_x + falling_piece_x + user_input_x
            #checks if it's greater than width and height of board
            if new_x < 0 or new_x >= BOARD_WIDTH or new_y >= BOARD_HEIGHT or new_y < 0:
                return True
            # 2. Add this to check for locked blocks!
            if new_y >= 0 and self.board[new_y][new_x] != 0:
                return True
        return False
    
    def move(self, user_input_y, user_input_x):
        """Attempts to move the piece. Returns True if successful."""
        if not self.check_collision(user_input_y, user_input_x):
            self.piece_y += user_input_y
            self.piece_x += user_input_x
            return True
        # The path was blocked. Do not change the coordinates.
        return False
    
    def lock_piece(self):
        """Permanently cements the active piece into the board array."""
        falling_piece = PIECES[self.current_piece][self.current_rotation]
        
        for dy, dx in falling_piece:
            lock_y = self.piece_y + dy
            lock_x = self.piece_x + dx
            
            # Make sure we don't try to lock a piece above the ceiling (y < 0)
            if 0 <= lock_y < BOARD_HEIGHT and 0 <= lock_x < BOARD_WIDTH:
                # Change the empty 0 to a solid 1
                self.board[lock_y][lock_x] = 1
                
        # Once cemented, check if we filled any rows, then spawn the next piece!
        self.clear_lines()
        self.spawn_piece()
    def clear_lines(self):
        """Removes full rows and drops new empty rows at the top."""
        new_board = [row for row in self.board if 0 in row]
        lines_cleared = BOARD_HEIGHT - len(new_board)
        
        if lines_cleared > 0:
            for _ in range(lines_cleared):
                new_board.insert(0, [0] * BOARD_WIDTH)
            self.board = new_board
            self.score += (lines_cleared * 100)

def curses_main(stdscr):
    curses.curs_set(0)    
    stdscr.nodelay(True)
    stdscr.keypad(True)     
    
    game = Tetris(stdscr)
    game.spawn_piece()
    last_fall_time = time.time()
    fall_speed = 0.5  # The piece falls every 0.5 seconds
    while not game.game_over:
        current_time = time.time()
        #Handle Gravity
        if current_time - last_fall_time > fall_speed:
            success = game.move(1, 0)
            if not success:
                game.spawn_piece()
            last_fall_time = current_time
            
        #Handle User Input
        key = stdscr.getch()
        if key != -1: # -1 means no key was pressed
            if key == curses.KEY_LEFT:
                game.move(0, -1)
            elif key == curses.KEY_RIGHT:
                game.move(0, 1)
            elif key == curses.KEY_DOWN:
                game.move(1, 0) # Move down faster
            elif key == ord('q'):
                break # Press 'q' to quit the loop and exit the game
        #Render the Frame
        game.draw()
        # Prevent the while loop from running millions of times a second and maxing out your CPU
        time.sleep(0.01)

def run_game():
    """The public function that starts the game."""
    # Notice how we just pass the name of the function, no parentheses!
    curses.wrapper(curses_main)
        