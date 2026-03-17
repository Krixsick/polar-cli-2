import typer
from files import files
import games

app = typer.Typer()

app.add_typer(files.app, name="files")
app.add_typer(games.app, name="games")
@app.command()
def hello():
    """Test to make sure the CLI is working."""
    print("Hello from polar-cli2!")

if __name__ == "__main__":
    app()