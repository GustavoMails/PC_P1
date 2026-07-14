"""
Repositorio para operaciones sobre productos.
"""

from sqlmodel import Session, select
from sqlalchemy.orm import selectinload  # Importante importar esto
from gamescout.database import get_engine
from gamescout.models import Product, ProductType


class ProductRepository:
    """
    Repositorio para acceder a la base de datos.
    """

    def __init__(self) -> None:
        self.engine = get_engine()

    def get_or_create_type(
        self,
        session: Session,
        name: str,
    ) -> ProductType:
        """
        Obtiene un tipo existente o lo crea.

        Args:
            session: Sesión activa.
            name: Nombre del tipo.

        Returns:
            ProductType encontrado o creado.
        """

        statement = select(ProductType).where(ProductType.name == name)

        product_type = session.exec(statement).first()

        if product_type is None:

            product_type = ProductType(name=name)

            session.add(product_type)

            session.commit()

            session.refresh(product_type)

        return product_type

    def upsert_products(self, products: list[dict]) -> None:
        """
        Inserta productos evitando duplicados.
        """
        with Session(self.engine) as session:
            for data in products:
                existing = session.exec(
                    select(Product).where(Product.product_id == data["product_id"])
                ).first()

                if existing:
                    continue

                product_type = self.get_or_create_type(session, data["type"])

                product = Product(
                    product_id=data["product_id"],
                    title=data["title"],
                    price_eur=data["price"],
                    type_id=product_type.id,
                )
                session.add(product)

            session.commit()

    def get_top_n(self, n: int) -> list[Product]:
        """
        Retorna los N productos más caros, incluyendo la relación con su tipo.
        """
        with Session(self.engine) as session:
            statement = (
                select(Product)
                .options(selectinload(Product.type))
                .order_by(Product.price_eur.desc())
                .limit(n)
            )
            return session.exec(statement).all()

    def get_products_by_type(self, type_name: str) -> list[Product]:
        """
        Obtiene todos los productos que pertenecen a un ProductType dado.
        """
        with Session(self.engine) as session:
            # Traemos el tipo cargando de forma ansiosa su lista de productos vinculados
            product_type = session.exec(
                select(ProductType)
                .options(selectinload(ProductType.products))
                .where(ProductType.name == type_name)
            ).first()

            if product_type is None:
                return []

            return product_type.products
