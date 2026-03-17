import hashlib
import platform
from typing import Annotated
import typer
import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from collections import defaultdict

app = typer.Typer(help="Files commands")
console = Console()

def get_file_hash(file_path, chunk_size=1024*1024):
    hasher = hashlib.sha224()
    with open(file_path, 'rb') as file:
        chunk = file.read(chunk_size)
        while chunk:
            hasher.update(chunk)
            chunk = file.read(chunk_size)
    return hasher.hexdigest()

@app.command()
def files_help():
    help_commands = {
        "files system-info": "Displays the specs of your computer/laptop"
        "files files-search <int> <size (mb/kb/gb)>"
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
def files_search(
    size: Annotated[float, typer.Argument(help="The size number (e.g. 500)")] = 100, 
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
        
@app.command()
def files_dupe(chunk_size: Annotated[float, typer.Option(help="Size of file you want to read")] = 1024 * 1024):
    path = os.getcwd()
    same_file_sizes = defaultdict(list)
    #store same size files in a list so "500mb: [w.txt, x.txt]"
    for curr_path, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('uv.lock')]
        for file in files:
            if file == "uv.lock" or file == "pyproject.toml" or file==".gitignore" or files == ".python--version" or file.endswith(".py"):
                continue
            curr_path = os.path.join(curr_path, file)
            try:
                file_size = os.path.getsize(curr_path)
                if file_size == 0: continue
                same_file_sizes[file_size].append(curr_path)
            except Exception as e:
                print(f"[dim]Could not read {curr_path}: {e}[/dim]")
    #get hashes for all files that are the same size only
    duplicates = defaultdict(list)
    for file_paths in same_file_sizes.values():
        if len(file_paths) > 1:
            for file_path in file_paths:
                file_hash_result = get_file_hash(file_path, chunk_size=1024 * 1024)
                duplicates[file_hash_result].append(file_path)
    #checks if it we have anything in our duplicate dictionary and prints anything that is inside
    found_any = False
    for file_hash, identical_files in duplicates.items():
        if len(identical_files) > 1: 
            found_any = True
            console.print(f"[bold red]Duplicate Group Found (Hash: {file_hash[:8]}...)[/bold red]")
            for f in identical_files:
                console.print(f"  - [cyan]{f}[/cyan]")
            console.print("") 

    if not found_any:
        console.print("[green]No duplicate files found! Your directory is clean.[/green]")
    
                
                
                
                
            
            
 
        
        