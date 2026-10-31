import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv


def connect() -> psycopg.Connection:
    """Open a connection; use as a context manager to commit or roll back."""
    load_dotenv(Path(__file__).resolve().parents[3] / ".env", override=False)
    required = ("POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB")
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        raise ValueError(f"Missing database settings: {', '.join(missing)}")

    return psycopg.connect(
        host=os.environ.get("POSTGRES_HOST", "127.0.0.1"),
        port=os.environ.get("POSTGRES_PORT", "5433"),
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        dbname=os.environ["POSTGRES_DB"],
        connect_timeout=5,
    )


if __name__ == "__main__":
    with connect() as connection:
        result = connection.execute("SELECT 1").fetchone()
        if result != (1,):
            raise RuntimeError("Unexpected database health check result")
    print("PostgreSQL connection OK")
