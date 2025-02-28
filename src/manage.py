import typer

from scripts.mock_data import apply_mock_data

app = typer.Typer()


@app.command()
def hello(name: str):
    print(f"Hello {name}")


@app.command()
def apply_mocks():
    apply_mock_data()


if __name__ == "__main__":
    app()
