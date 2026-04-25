"""
EJERCICIO 3: Automatizar una busqueda en Google
===============================================
Objetivo: Escribir texto, presionar Enter, leer resultados.

Conceptos cubiertos:
- send_keys() para escribir texto
- Keys.RETURN para presionar Enter
- Leer texto de elementos con .text
- WebDriverWait para esperar resultados
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 10)  # Esperar hasta 10 segundos

print("Abriendo Google...")
driver.get("https://www.google.com")

# Paso 1: Encontrar el campo de busqueda
campo_busqueda = driver.find_element(By.NAME, "q")

# Paso 2: Escribir la busqueda
termino = "Python Selenium tutorial en espanol"
campo_busqueda.send_keys(termino)
print(f"Buscando: '{termino}'")

# Paso 3: Presionar Enter
campo_busqueda.send_keys(Keys.RETURN)

# Paso 4: Esperar a que carguen los resultados
wait.until(EC.presence_of_element_located((By.ID, "search")))
print("Resultados cargados!")

# Paso 5: Leer los titulos de los resultados
# Los titulos de resultados de Google son etiquetas <h3>
titulos = driver.find_elements(By.TAG_NAME, "h3")

print(f"\nSe encontraron {len(titulos)} encabezados.")
print("\nPrimeros 5 resultados:")
print("-" * 50)
for i, titulo in enumerate(titulos[:5], 1):
    if titulo.text:  # Algunos h3 pueden estar vacios
        print(f"{i}. {titulo.text}")

print("-" * 50)
print(f"\nURL actual: {driver.current_url}")

driver.quit()
print("\nEjercicio 3 completado!")


# ============================================================
# DESAFIO PARA EL ALUMNO:
# Cambia el termino de busqueda por algo de tu interes.
# Imprime los primeros 10 resultados.
# ============================================================
