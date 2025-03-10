import typer

from scripts.migrations import apply_migrations
from scripts.mock_data import apply_mock_data

app = typer.Typer()


@app.command()
def apply_mocks():
    apply_mock_data()


@app.command()
def migrate():
    apply_migrations()


if __name__ == "__main__":
    app()
