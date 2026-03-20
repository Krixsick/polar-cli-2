import typer 
import time
from rich.progress import Progress

app = typer.Typer(help="Productivity Tools")

@app.command()
def pomodoro(minutes: int = 25):
    total_seconds = minutes * 60
    with Progress() as progress:
        task = progress.add_task(f"[cyan]Focusing for {minutes} mins", total=total_seconds)
        while not progress.finished:
            time.sleep(1)
            progress.update(task, advance=1)
            
    print("ime's up! Take a break.")
