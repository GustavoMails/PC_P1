"""
Configuración de la base de datos SQLite.
"""

from sqlmodel import SQLModel, create_engine  # type: ignore

DATABASE_URL = "sqlite:///data/gamescout.db"

engine = create_engine(
    DATABASE_URL,
    echo=False,
)


def get_engine():
    """
    Retorna el motor de la base de datos.

    Returns:
        Engine: Motor SQLite.
    """
    return engine


def create_db_and_tables() -> None:
    """
    Crea todas las tablas definidas en los modelos.
    """
    SQLModel.metadata.create_all(engine)
