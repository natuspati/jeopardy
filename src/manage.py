import typer

from scripts.migrations import apply_migrations
from scripts.mock_data import apply_mock_data
from scripts.path_utils import ensure_working_directory

app = typer.Typer()


@app.command()
def hello(name: str):
    print(f"Hello {name}")


@app.command()
def apply_mocks():
    apply_mock_data()


@app.command()
def migrate():
    apply_migrations()


if __name__ == "__main__":
    ensure_working_directory()
    app()
