"""
Modelos de datos para GameScout.
"""

from datetime import datetime
from typing import Optional, List  # <-- List con L mayúscula

from sqlmodel import Field, Relationship, SQLModel  # type: ignore


class Product(SQLModel, table=True):
    """
    Representa un producto extraído del sitio web.
    """

    id: Optional[int] = Field(default=None, primary_key=True)

    product_id: int = Field(index=True, ge=1)
    title: str = Field(min_length=1)
    price_eur: float = Field(ge=0)

    scraped_at: datetime = Field(default_factory=datetime.now)

    type_id: Optional[int] = Field(
        default=None,
        foreign_key="producttype.id",
    )

    type: Optional["ProductType"] = Relationship(back_populates="products")


class ProductType(SQLModel, table=True):
    """
    Representa un tipo o categoría de producto.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(min_length=1, unique=True)

    products: List[Product] = Relationship(
        back_populates="type", sa_relationship_kwargs={"lazy": "selectin"}
    )
