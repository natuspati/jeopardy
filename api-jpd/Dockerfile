FROM astral/uv:python3.12-bookworm-slim

ARG WORKDIR=/opt/sjf-sage-api
WORKDIR $WORKDIR

COPY ./pyproject.toml ./uv.lock ./
RUN uv sync --frozen --no-dev

COPY ./src/ $WORKDIR/

CMD ["uv", "run", "--no-sync", "main.py"]
