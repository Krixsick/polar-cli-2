
import curses
import random
import time
#Constants
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
CELL_WIDTH = 2  

# Map each piece type to a curses color pair index (used for colored blocks)
PIECE_COLORS = {
    "I": 1,
    "O": 2,
    "T": 3,
    "S": 4,
    "Z": 5,
    "L": 6,
    "J": 7,
}

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
        # If the new piece immediately overlaps locked blocks, the game is over
        if self.check_collision(0, 0):
            self.game_over = True
    
    def draw(self):
            self.stdscr.erase()
            # Offsets so the board isn't jammed into the corner
            offset_x = 2
            offset_y = 2
            board_width_chars = BOARD_WIDTH * CELL_WIDTH
            # Top border
            self.stdscr.addstr(offset_y, offset_x, "+" + "-" * board_width_chars + "+")

            # Draw each row of the board
            for row in range(BOARD_HEIGHT):
                self.stdscr.addstr(offset_y + 1 + row, offset_x, "|")  # left wall
                self.stdscr.addstr(offset_y + 1 + row, offset_x + 1 + board_width_chars, "|")  # right wall
                for col in range(BOARD_WIDTH):
                    cell = self.board[row][col]
                    x_pos = offset_x + 1 + col * CELL_WIDTH
                    y_pos = offset_y + 1 + row
                    if cell > 0:
                        # Locked block: draw 2 colored spaces
                        self.stdscr.addstr(y_pos, x_pos, "  ", curses.color_pair(cell))
                    else:
                        # Empty cell: draw a dot grid so you can see the board
                        self.stdscr.addstr(y_pos, x_pos, " .")

            # Bottom border
            self.stdscr.addstr(offset_y + 1 + BOARD_HEIGHT, offset_x, "+" + "-" * board_width_chars + "+")

            # Draw the current falling piece
            if self.current_piece:
                falling_piece = PIECES[self.current_piece][self.current_rotation]
                color = PIECE_COLORS[self.current_piece]
                for y, x in falling_piece:
                    new_y = y + self.piece_y
                    new_x = x + self.piece_x
                    if 0 <= new_y < BOARD_HEIGHT and 0 <= new_x < BOARD_WIDTH:
                        self.stdscr.addstr(
                            offset_y + 1 + new_y,
                            offset_x + 1 + new_x * CELL_WIDTH,
                            "  ",
                            curses.color_pair(color),
                        )

            # Info panel to the right of the board
            info_x = offset_x + board_width_chars + 4
            self.stdscr.addstr(offset_y + 1, info_x, f"Score: {self.score}")
            # Controls
            self.stdscr.addstr(offset_y + 4, info_x, "Controls:")
            self.stdscr.addstr(offset_y + 5, info_x, "  Left/Right  Move")
            self.stdscr.addstr(offset_y + 6, info_x, "  Up          Rotate")
            self.stdscr.addstr(offset_y + 7, info_x, "  Down        Soft drop")
            self.stdscr.addstr(offset_y + 8, info_x, "  q           Quit")

            self.stdscr.refresh()

    def rotate(self):
        """Try to rotate the piece. If the rotated position collides, don't rotate."""
        # Cycle to the next rotation state (wraps around with %)
        new_rotation = (self.current_rotation + 1) % len(PIECES[self.current_piece])
        # Check if the rotated piece would collide with anything
        rotated_shape = PIECES[self.current_piece][new_rotation]
        for dy, dx in rotated_shape:
            new_y = self.piece_y + dy
            new_x = self.piece_x + dx
            if new_x < 0 or new_x >= BOARD_WIDTH or new_y >= BOARD_HEIGHT or new_y < 0:
                return  # Would go out of bounds, so don't rotate
            if new_y >= 0 and self.board[new_y][new_x] != 0:
                return  # Would overlap a locked block, so don't rotate
        # No collision — apply the rotation
        self.current_rotation = new_rotation

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
                # Store the color index so locked blocks keep their color
                self.board[lock_y][lock_x] = PIECE_COLORS[self.current_piece]
                
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
            # Bonus points for clearing more lines at once (like real Tetris)
            points = {1: 100, 2: 300, 3: 500, 4: 800}
            self.score += points.get(lines_cleared, 800)

def init_colors():
    """Set up curses color pairs so each piece type has its own color."""
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLUE)       # I
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_YELLOW)   # O
    curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_MAGENTA) # T
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_GREEN)     # S
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_RED)         # Z
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_WHITE)     # L
    curses.init_pair(7, curses.COLOR_CYAN, curses.COLOR_CYAN)       # J

def curses_main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)
    init_colors()

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
                game.lock_piece()
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
            elif key == curses.KEY_UP:
                game.rotate()
            elif key == ord('q'):
                break # Press 'q' to quit the loop and exit the game
        #Render the Frame
        game.draw()
        # Prevent the while loop from running millions of times a second and maxing out your CPU
        time.sleep(0.01)

    # Game Over Screen
    if game.game_over:
        stdscr.nodelay(False)  # Make getch() wait for a keypress again
        stdscr.clear()
        stdscr.addstr(10, 5, "GAME OVER!", curses.A_BOLD)
        stdscr.addstr(12, 5, f"Final Score: {game.score}")
        stdscr.addstr(14, 5, "Press any key to exit.")
        stdscr.refresh()
        stdscr.getch()

def run_game():
    """The public function that starts the game."""
    
    curses.wrapper(curses_main)
        