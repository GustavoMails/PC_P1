"""
Scraper para obtener productos desde Oxylabs Sandbox.
"""

from __future__ import annotations
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class ProductScraper:
    """
    Scraper de productos utilizando Selenium.
    """

    BASE_URL = "https://sandbox.oxylabs.io/products"

    def __init__(self) -> None:
        """
        Inicializa el navegador en modo headless.
        """
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options,
        )

    def scrape(self) -> list[dict]:
        """
        Extrae los productos de las primeras 5 páginas.

        Returns:
            Lista de productos.
        """

        products = []

        wait = WebDriverWait(self.driver, 10)

        for page in range(1, 6):

            url = f"{self.BASE_URL}?page={page}"

            self.driver.get(url)

            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".products-wrapper")))

            cards = self.driver.find_elements(
                By.CSS_SELECTOR,
                ".product-card",
            )

            print(f"Página {page}: {len(cards)} productos")

            for card in cards:

                try:

                    href = card.find_element(
                        By.TAG_NAME,
                        "a",
                    ).get_attribute("href")

                    product_id = int(href.rstrip("/").split("/")[-1])

                    title = card.find_element(
                        By.CSS_SELECTOR,
                        ".title",
                    ).text.strip()

                    category = card.find_elements(
                        By.CSS_SELECTOR,
                        ".category span",
                    )[0].text.strip()

                    price = card.find_element(
                        By.CSS_SELECTOR,
                        ".price-wrapper",
                    ).text

                    price = price.replace("€", "").replace(",", ".").strip()

                    price = float(price)

                    products.append(
                        {
                            "product_id": product_id,
                            "title": title,
                            "type": category,
                            "price": price,
                        }
                    )

                except Exception as e:

                    logging.warning(e)

                    continue

        return products

    def close(self) -> None:
        """
        Cierra el navegador.
        """
        self.driver.quit()
