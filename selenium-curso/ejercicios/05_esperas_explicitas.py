"""
EJERCICIO 5: Esperas Explicitas
================================
Objetivo: Aprender la diferencia entre esperas y por que importan.

Conceptos cubiertos:
- time.sleep() - por que es mala practica
- implicitly_wait() - espera implicita
- WebDriverWait + expected_conditions - espera explicita (LA CORRECTA)
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# ---- DEMO: ESPERA EXPLICITA EN ACCION ----
print("Demo de esperas con el sitio de practica...")
driver.get("https://practicetestautomation.com/practice-test-login/")

# ESPERA EXPLICITA - Esperamos hasta que el boton sea clickeable
wait = WebDriverWait(driver, 10)

print("Esperando a que el boton de submit sea clickeable...")
boton = wait.until(
    EC.element_to_be_clickable((By.ID, "submit"))
)
print(f"Boton encontrado y listo: '{boton.get_attribute('value')}'")

# ---- DIFERENTES CONDICIONES DE ESPERA ----
print("\n--- Condiciones de espera disponibles ---")

# 1. Esperar a que el elemento exista (aunque sea invisible)
elemento = wait.until(
    EC.presence_of_element_located((By.ID, "username"))
)
print(f"1. presence_of_element_located: campo '{elemento.get_attribute('id')}' existe")

# 2. Esperar a que el elemento sea visible
elemento = wait.until(
    EC.visibility_of_element_located((By.ID, "password"))
)
print(f"2. visibility_of_element_located: campo '{elemento.get_attribute('id')}' es visible")

# 3. Esperar a que el titulo de la pagina contenga texto
wait.until(EC.title_contains("Login"))
print(f"3. title_contains: titulo es '{driver.title}'")

# 4. Esperar a que la URL contenga texto
wait.until(EC.url_contains("practice-test-login"))
print(f"4. url_contains: URL es '{driver.current_url[:50]}...'")

# ---- COMPARACION: CON Y SIN ESPERA ----
print("\n--- Hacemos login para ver espera de resultado ---")

driver.find_element(By.ID, "username").send_keys("student")
driver.find_element(By.ID, "password").send_keys("Password123")
driver.find_element(By.ID, "submit").click()

# SIN ESPERA (puede fallar en conexion lenta):
# titulo = driver.find_element(By.TAG_NAME, "h1").text  # PELIGROSO

# CON ESPERA EXPLICITA (siempre seguro):
titulo_elemento = wait.until(
    EC.presence_of_element_located((By.TAG_NAME, "h1"))
)
print(f"Titulo con espera explicita: '{titulo_elemento.text}'")

driver.quit()
print("\nEjercicio 5 completado!")


# ============================================================
# REGLA DE ORO:
# - Nunca uses time.sleep() en tests de produccion
# - Configura implicitly_wait UNA vez al crear el driver
# - Usa WebDriverWait para condiciones especificas
# ============================================================
