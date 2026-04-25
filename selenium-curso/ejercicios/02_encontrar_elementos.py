"""
EJERCICIO 2: Encontrar elementos en la pagina
==============================================
Objetivo: Usar diferentes locators para encontrar elementos.

Conceptos cubiertos:
- By.ID
- By.NAME
- By.CLASS_NAME
- By.TAG_NAME
- find_element vs find_elements
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# ----- EJEMPLO 1: Buscar por NAME -----
print("\n--- EJEMPLO 1: Buscar por NAME ---")
driver.get("https://www.google.com")
time.sleep(1)

# El campo de busqueda de Google tiene name="q"
campo = driver.find_element(By.NAME, "q")
print(f"Campo encontrado: {campo.tag_name}")  # Debe imprimir "input"

# ----- EJEMPLO 2: Contar elementos con find_elements -----
print("\n--- EJEMPLO 2: Contar elementos ---")
# Contar todos los links en la pagina
todos_los_links = driver.find_elements(By.TAG_NAME, "a")
print(f"Hay {len(todos_los_links)} links en google.com")

# ----- EJEMPLO 3: Buscar por XPATH -----
print("\n--- EJEMPLO 3: XPath ---")
# Buscar el boton "Buscar con Google" por su valor
try:
    boton = driver.find_element(By.XPATH, "//input[@value='Buscar con Google']")
    print(f"Boton encontrado: {boton.get_attribute('value')}")
except:
    print("(Boton no visible - Google oculta el boton cuando hay texto)")

# ----- EJEMPLO 4: find_element vs find_elements -----
print("\n--- EJEMPLO 4: find_element vs find_elements ---")

# find_elements siempre devuelve lista, nunca da error si no encuentra
elementos = driver.find_elements(By.ID, "id-que-no-existe")
print(f"find_elements con ID inexistente devuelve: {elementos}")  # []

# find_element lanza excepcion si no encuentra
try:
    driver.find_element(By.ID, "id-que-no-existe")
except Exception as e:
    print(f"find_element con ID inexistente lanza: {type(e).__name__}")


time.sleep(2)
driver.quit()
print("\nEjercicio 2 completado!")


# ============================================================
# DESAFIO PARA EL ALUMNO:
# 1. Ve a tu sitio favorito
# 2. Inspecciona un elemento (click derecho -> Inspeccionar)
# 3. Encuentra el elemento usando By.ID, By.NAME o By.CLASS_NAME
# 4. Imprime su texto con elemento.text
# ============================================================
