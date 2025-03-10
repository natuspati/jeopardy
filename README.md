# Project Name
Jeopardy

## Description
TBD

### Cloning the Repository
To get started, clone the repository:
```sh
git clone https://github.com/natuspati/jeopardy.git
cd jeopardy
```

## Deploy
Use environment variable templates in [`deploy`](deploy).

### Local Deployment
To run the project locally, follow these steps:

1. Install dependencies using `uv`:
   ```sh
   uv uv python install pypy@3.12
   uv venv
   uv init
   ```
2. Activate the virtual environment:
   ```sh
   source .venv/bin/activate
   ```
3. Create local environment variables from [`deploy/local.env`](deploy/local.env) as `.env`
   in [`src`](src) directory.
4. Start the application:
   ```sh
   cd src
   python main.py
   ```

### Remote Deployment (TBD)
Details for remote deployment are to be determined.

## CLI
This project provides a command-line interface (CLI) built using the `Typer`.
See [`src/manage.py`](src/manage.py)

### Usage
Run the CLI with the following command:
```sh
python src/manage.py --help
```
### Commands
- `migrate` - apply alembic migrations
- `apply-mocks` - add mock mock data
