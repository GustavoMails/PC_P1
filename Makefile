# Configuración de variables
PYTHON = python
MODULE = gamescout

.PHONY: install lint format run test

# 1. Instalar dependencias (asume que el entorno conda ya está creado/activo)
install:
	pip install --upgrade pip
	pip install flake8 black pytest selenium webdriver-manager sqlmodel

# 2. Verificar estilo y errores de código con flake8 (largo máximo de línea 100)
lint:
	flake8 $(MODULE) tests --max-line-length=100

# 3. Formatear automáticamente el código usando black
format:
	black $(MODULE) tests --line-length=100

# 4. Ejecutar el pipeline principal del proyecto
run:
	$(PYTHON) -m $(MODULE).main

# 5. Ejecutar la suite de pruebas unitarias con pytest
test:
	$(PYTHON) -m pytest tests/

# 6. Ejecutar el dashboard de Streamlit
dashboard:
	streamlit run app/dashboard.py