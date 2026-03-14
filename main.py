import typer
from files import files


app = typer.Typer()

app.add_typer(files.app, name="files")

@app.command()
def hello():
    """Test to make sure the CLI is working."""
    print("Hello from polar-cli2!")

if __name__ == "__main__":
    app()