import platform
from typing import Annotated
import typer
import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

app = typer.Typer(help="Files")
console = Console()

@app.command()
def files_help():
    help_commands = {
        "files system-info": "Displays the specs of your computer/laptop"
        "files file-search <int> <size (mb/kb/gb)>"
    }
    
    table = Table(show_header=False, padding=(0, 2))
    table.add_column("Command", style="bold cyan", justify="right")
    table.add_column("Description", style="bold cyan", justify="right")
    
    for command, description in help_commands.items():
        table.add_row(command, description)

    console.print(Panel(
        table,
        title="[bold]Files Help Commands[/]",
        border_style="cyan",
        padding=(1, 1),
    ))
    
@app.command()
def system_info():
    info = {
        "System": platform.system(),
        "Node": platform.node(),
        "Release": platform.release(),
        "Machine": platform.machine(),
        "Python": platform.python_version(),
    }
    table = Table(show_header=False, padding=(0, 2))
    table.add_column("Key", style="bold cyan", justify="right")
    table.add_column("Value", style="white")

    for key, value in info.items():
        table.add_row(key, value)

    console.print(Panel(
        table,
        title="[bold]System Information[/]",
        border_style="cyan",
        padding=(1, 1),
    ))
@app.command()
def file_search(
    size: Annotated[float, typer.Argument(help="The size number (e.g. 500)")], 
    unit: Annotated[str, typer.Argument(help="mb, gb, or kb")] = "mb"
):
    """Finds files in the current directory larger than the specified size."""
    multiplier = 1
    unit = unit.lower()
    
    if unit in ["gb", "g"]:
        multiplier = 1024 * 1024 * 1024
    elif unit in ["mb", "m"]:
        multiplier = 1024 * 1024
    elif unit in ["kb", "k"]:
        multiplier = 1024
    target_bytes = size * multiplier
    found_any = False
    path = os.getcwd()

    console.print(f"[dim]Scanning {path} for files larger than {size}{unit}...[/dim]\n")
    for curr_path, dirs, files in os.walk(path):
        for file_name in files:
            file_path = os.path.join(curr_path, file_name)
            try:
                file_size = os.path.getsize(file_path)
                if file_size > target_bytes:
                    readable_size = f"{file_size / (1024*1024):.2f} MB"
                    console.print(f"  - {file_path} [bold cyan]({readable_size})[/bold cyan]")
                    found_any = True
            except Exception:
                pass
                
    if not found_any:
        console.print("[yellow]No files found.[/yellow]")
 
        
        