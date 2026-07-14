# GameScout - Pipeline de Extracción y Persistencia Relacional

Este proyecto es una herramienta automatizada desarrollada en Python para la extracción de datos (*web scraping*) de un sandbox de comercio electrónico de videojuegos. Los datos recolectados se procesan y almacenan en una base de datos relacional SQLite utilizando **SQLModel** (basado en SQLAlchemy y Pydantic), permitiendo realizar consultas interactivas avanzadas a través de la consola.

El proyecto cumple estrictamente con los lineamientos, buenas prácticas de desarrollo y rúbrica de evaluación de la **UCN 2026**.

---

## 🛠️ Requisitos Previos

Antes de comenzar, asegúrate de tener instalado en tu sistema:
- **Miniconda** o **Anaconda**
- **Make** (herramienta de automatización de comandos)
- **Google Chrome** (necesario para el funcionamiento de Selenium Headless)

---

## 🚀 Instalación y Configuración

Sigue estos pasos en tu terminal para preparar el entorno virtual e instalar las dependencias necesarias:

1. **Crear y activar el entorno Conda:**
   ```bash
   conda create --name PRUEBA-P1 python=3.10 -y
   conda activate PRUEBA-P1