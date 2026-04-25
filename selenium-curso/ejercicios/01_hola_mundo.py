"""
EJERCICIO 1: Hola Mundo de Selenium
====================================
Objetivo: Abrir un navegador, ir a una pagina, cerrar el navegador.

Conceptos cubiertos:
- Importar Selenium
- Crear y configurar el WebDriver
- Abrir una URL
- Cerrar el navegador
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# 1. Crear el driver (esto abre Chrome)
print("Abriendo Chrome...")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# 2. Navegar a una URL
driver.get("https://www.google.com")
print(f"Pagina abierta: {driver.title}")

# 3. Esperar para que puedan verlo
time.sleep(3)

# 4. Cerrar el navegador
driver.quit()
print("Navegador cerrado. Script completado!")


# ============================================================
# DESAFIO PARA EL ALUMNO:
# Cambia la URL por tu sitio favorito y ejecuta de nuevo.
# Imprime el titulo de esa pagina.
# ============================================================
