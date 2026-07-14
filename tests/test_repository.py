"""
Pruebas unitarias para el repositorio de productos.
"""

import pytest
from sqlmodel import SQLModel, Session, create_engine

from gamescout.models import Product, ProductType
from gamescout.repository import ProductRepository


@pytest.fixture(name="repo")
def fixture_repo():
    """
    Fixture que inicializa un repositorio apuntando a una BD en memoria.
    """
    # Creamos un motor temporal en memoria para aislamiento absoluto
    engine = create_engine("sqlite:///:memory:", echo=False)
    SQLModel.metadata.create_all(engine)

    repository = ProductRepository()
    repository.engine = engine  # Reemplazamos el motor real por el de pruebas

    return repository


def test_get_or_create_type(repo: ProductRepository) -> None:
    """
    Prueba que get_or_create_type busque por nombre y no duplique tipos.
    """
    with Session(repo.engine) as session:
        # 1. Crear por primera vez
        tipo1 = repo.get_or_create_type(session, "RPG")
        assert tipo1.id is not None
        assert tipo1.name == "RPG"

        # 2. Intentar crear el mismo tipo de nuevo
        tipo2 = repo.get_or_create_type(session, "RPG")
        assert tipo1.id == tipo2.id  # Deben ser el mismo registro (no duplicado)


def test_upsert_products_and_avoid_duplicates(repo: ProductRepository) -> None:
    """
    Prueba que upsert_products guarde datos y evite duplicados por product_id.
    """
    productos_mock = [
        {"product_id": 101, "title": "Zelda", "price": 59.99, "type": "Aventura"},
        {"product_id": 102, "title": "Mario", "price": 49.99, "type": "Plataformas"},
    ]

    # 1. Primera inserción
    repo.upsert_products(productos_mock)

    with Session(repo.engine) as session:
        from sqlmodel import select
        db_products = session.exec(select(Product)).all()
        assert len(db_products) == 2

    # 2. Re-insertar para verificar control de duplicados (upsert)
    repo.upsert_products(productos_mock)

    with Session(repo.engine) as session:
        db_products_after = session.exec(select(Product)).all()
        assert len(db_products_after) == 2  # Sigue siendo 2, no se duplicaron


def test_get_top_n(repo: ProductRepository) -> None:
    """
    Prueba que get_top_n retorne los productos más caros usando su relación.
    """
    productos_mock = [
        {"product_id": 1, "title": "Barato", "price": 10.0, "type": "Indie"},
        {"product_id": 2, "title": "Caro", "price": 90.0, "type": "AAA"},
        {"product_id": 3, "title": "Medio", "price": 50.0, "type": "Indie"},
    ]
    repo.upsert_products(productos_mock)

    top_2 = repo.get_top_n(2)

    assert len(top_2) == 2
    assert top_2[0].title == "Caro"      # El más caro primero
    assert top_2[1].title == "Medio"     # El segundo más caro
    assert top_2[0].type.name == "AAA"   # Verifica que la relación sea navegable


def test_get_products_by_type(repo: ProductRepository) -> None:
    """
    Prueba que get_products_by_type filtre correctamente por categoría.
    """
    productos_mock = [
        {"product_id": 1, "title": "Elden Ring", "price": 60.0, "type": "RPG"},
        {"product_id": 2, "title": "Fifa", "price": 70.0, "type": "Deportes"},
        {"product_id": 3, "title": "Skyrim", "price": 30.0, "type": "RPG"},
    ]
    repo.upsert_products(productos_mock)

    juegos_rpg = repo.get_products_by_type("RPG")

    assert len(juegos_rpg) == 2
    titulos = [juego.title for juego in juegos_rpg]
    assert "Elden Ring" in titulos
    assert "Skyrim" in titulos