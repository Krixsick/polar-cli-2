import typer
from .tetris import run_game

app = typer.Typer(help="Terminal games.")

@app.command(name="tetris")
def play_tetris():
    """Launch terminal Tetris!"""
    # Call the new runner function
    run_game()