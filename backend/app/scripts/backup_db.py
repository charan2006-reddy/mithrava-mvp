"""Database backup utility — creates compressed SQL dumps.

Run with:
    python -m app.scripts.backup_db

Requires: psycopg2 (already in requirements.txt) for pg_dump-compatible output.
For production, prefer the shell script (backup_db.sh) which uses pg_dump directly.
"""

import asyncio
import gzip
import logging
import os
import sys
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("mithrava.backup")


async def backup_sqlite(output_path: str) -> str:
    """Backup an SQLite database (copy file)."""
    db_url = os.getenv("DATABASE_URL", "")
    if "sqlite" not in db_url:
        raise ValueError("Not an SQLite database")

    # Extract path from URL
    db_path = db_url.split("///")[-1]
    if db_path == ":memory:":
        raise ValueError("Cannot backup in-memory SQLite database")

    if not os.path.exists(db_path):
        raise FileNotFoundError(f"SQLite database not found: {db_path}")

    import shutil
    with open(db_path, "rb") as src:
        with gzip.open(output_path, "wb") as dst:
            dst.write(src.read())

    size = os.path.getsize(output_path)
    logger.info(f"  SQLite backup: {output_path} ({size:,} bytes)")
    return output_path


async def backup_postgres(output_path: str) -> str:
    """Backup a PostgreSQL database using asyncpg dumps a SQL dump file."""
    import subprocess

    db_url = os.getenv("DATABASE_URL", "")
    # Parse connection details from URL
    # postgresql+asyncpg://user:pass@host:port/dbname
    url = db_url.replace("+asyncpg", "").replace("+psycopg2", "")

    # Extract parts
    without_prefix = url.split("://", 1)[1]
    auth, host_db = without_prefix.split("@", 1)
    user, password = auth.split(":", 1)
    host_port, dbname = host_db.split("/", 1)
    host, port = host_port.split(":", 1) if ":" in host_port else (host_port, "5432")

    # Use pg_dump via subprocess
    env = os.environ.copy()
    env["PGPASSWORD"] = password

    cmd = [
        "pg_dump",
        "-h", host,
        "-p", port,
        "-U", user,
        "-d", dbname,
        "--no-owner",
        "--no-privileges",
        "--clean",
        "--if-exists",
        "-F", "p",
    ]

    try:
        result = subprocess.run(
            cmd, env=env, capture_output=True, text=True, timeout=300
        )
        if result.returncode != 0:
            raise RuntimeError(f"pg_dump failed: {result.stderr}")

        with gzip.open(output_path, "wt") as f:
            f.write(result.stdout)

        size = os.path.getsize(output_path)
        logger.info(f"  PostgreSQL backup: {output_path} ({size:,} bytes)")
        return output_path

    except FileNotFoundError:
        raise RuntimeError(
            "pg_dump not found. Install postgresql-client:\n"
            "  Ubuntu/Debian: apt-get install postgresql-client\n"
            "  macOS: brew install postgresql"
        )


async def main():
    """Create a timestamped database backup."""
    try:
        from dotenv import load_dotenv
        load_dotenv(override=True)
    except ImportError:
        pass

    db_url = os.getenv("DATABASE_URL", "")
    backup_dir = os.getenv("BACKUP_DIR", "./backups")
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(backup_dir, f"mithrava_{timestamp}.sql.gz")

    logger.info("Creating database backup...")

    if "sqlite" in db_url.lower():
        await backup_sqlite(output_path)
    elif "postgresql" in db_url.lower():
        await backup_postgres(output_path)
    else:
        logger.error(f"Unsupported database URL: {db_url}")
        sys.exit(1)

    logger.info("Backup complete!")


if __name__ == "__main__":
    asyncio.run(main())
