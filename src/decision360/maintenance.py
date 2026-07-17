"""Safe backup and integrity operations for the reference SQLite store."""

from __future__ import annotations

import argparse
import sqlite3
from contextlib import closing
from pathlib import Path

from .store import SQLiteStore


def backup_database(source: Path, target: Path) -> None:
    if source.resolve() == target.resolve():
        raise ValueError("Backup target must differ from the source database")
    if not source.is_file():
        raise FileNotFoundError(source)
    target.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(source)) as source_connection, closing(sqlite3.connect(target)) as target_connection:
        with target_connection:
            source_connection.backup(target_connection)


def verify_database(path: Path) -> bool:
    store = SQLiteStore(path)
    with store.connect() as connection:
        sqlite_ok = connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    return sqlite_ok and store.verify_audit_integrity()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    backup = commands.add_parser("backup")
    backup.add_argument("source", type=Path)
    backup.add_argument("target", type=Path)
    verify = commands.add_parser("verify")
    verify.add_argument("database", type=Path)
    args = parser.parse_args()
    if args.command == "backup":
        backup_database(args.source, args.target)
        print(f"Backup written to {args.target}")
        return 0
    valid = verify_database(args.database)
    print("valid" if valid else "invalid")
    return 0 if valid else 1
