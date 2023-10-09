import datetime
import shutil
import sqlite3
from typing import Optional, Tuple

from mathgen import MathProblemModel, MathProblemModelAdapter
from pydantic import ValidationError

from . import config, utils

DBC: sqlite3.Connection


def __row_dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


@utils.on_startup()
def connect_db():
    global DBC
    DBC = sqlite3.connect(config.DB_PATH)
    DBC.row_factory = __row_dict_factory
    DBC.autocommit = True
    return DBC


def close_db():
    global DBC
    DBC.close()


MODELS_TABLE = "models"

x = "\n".join(
    [
        "@var a = rand(3, 100) / rand(3, 10)",
        "@var b = rand(3, 100) / rand(3, 10)",
        "@condition a < 10 and b < 10 and is_improper(a, b)",
        "@question {a} \\times {b}?",
        "@answer {a * b}",
    ]
)


BUILD_STMTS = [
    f"""
    CREATE TABLE {MODELS_TABLE} (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        code TEXT NOT NULL
    )
    """
]


def rebuild_db():
    global DBC
    close_db()
    backup_name = datetime.datetime.now().strftime(r"main-backup-%Y%m%d%H%M%S")
    base_backup_path = config.get_backups_dir().joinpath(f"./{backup_name}")
    backup_path = base_backup_path.with_suffix(".db")
    backup_id_count = 0
    while backup_path.exists():
        backup_id_count += 1
        backup_path = base_backup_path.with_name(
            base_backup_path.name + f" ({backup_id_count})"
        ).with_suffix(".db")
    shutil.copyfile(config.DB_PATH, backup_path)
    config.DB_PATH.unlink()
    connect_db()
    for stmt in BUILD_STMTS:
        DBC.execute(stmt)

    DBC.execute(f"INSERT INTO {MODELS_TABLE} (name, code) VALUES ('test', ?)", (x,))

    print(f"Reset db -- Backup stored at: {backup_path}")


def get_model(model_name: str) -> Tuple[Optional[MathProblemModel], Optional[str]]:
    result: Optional[sqlite3.Row] = DBC.execute(
        f"SELECT * FROM {MODELS_TABLE} WHERE name = ?", (model_name,)
    ).fetchone()
    if result is None:
        return (None, f"Model {model_name} not found.")

    try:
        return (MathProblemModelAdapter.validate_python(result), None)
    except ValidationError as e:
        return (None, f"Model {model_name} is invalid: {e}")
