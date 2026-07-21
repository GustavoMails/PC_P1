"""
Pipeline principal interactivo para GameScout.
"""

from gamescout.database import create_db_and_tables
from gamescout.repository import ProductRepository
from gamescout.scraper import ProductScraper


def main() -> None:
    """
    Ejecuta el flujo interactivo de extracción y consulta de productos.
    """
    # 1. Inicialización y Scraping
    create_db_and_tables()

    scraper = ProductScraper()
    products = scraper.scrape()
    scraper.close()

    repo = ProductRepository()
    repo.upsert_products(products)

    print(f"\n[Éxito] Se procesaron y guardaron {len(products)} productos.")
    print("-" * 50)

    # 2. Interacción por consola: Consulta de los N más caros
    try:
        n_input = input("Ingresa la cantidad (N) de productos más caros que deseas ver: ")
        n = int(n_input)
    except ValueError:
        print("[Aviso] Entrada no válida. Se mostrará el Top 5 por defecto.")
        n = 5

    print(f"\n--- Top {n} productos más caros ---")
    top_products = repo.get_top_n(n)

    if not top_products:
        print("No hay productos registrados en la base de datos.")
    for product in top_products:
        print(
            f"* {product.title} - "
            f"{product.price_eur:.2f} € - "
            f"[{product.type.name}]"
        )

    print("-" * 50)

    # 3. Interacción por consola: Consulta por tipo de juego
    tipo_buscado = input("Ingresa el tipo de juego que deseas buscar (ej. Action, RPG): ").strip()

    print(f"\n--- Productos de la categoría: '{tipo_buscado}' ---")
    products_by_type = repo.get_products_by_type(tipo_buscado)

    if not products_by_type:
        print(f"No se encontraron productos para la categoría '{tipo_buscado}'.")
    else:
        print(f"Se encontraron {len(products_by_type)} productos:")
        for product in products_by_type:
            print(f"- {product.title} ({product.price_eur:.2f} €)")


if __name__ == "__main__":
    main()
