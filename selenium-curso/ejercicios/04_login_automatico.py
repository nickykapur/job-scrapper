"""
EJERCICIO 4: Login Automatizado
================================
Objetivo: Llenar un formulario de login y verificar el resultado.

Sitio: https://practicetestautomation.com/practice-test-login/
Usuario: student
Contrasena: Password123

Conceptos cubiertos:
- Llenar formularios
- Hacer click en botones
- WebDriverWait para esperar resultados
- Verificar texto en la pagina
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

URL = "https://practicetestautomation.com/practice-test-login/"
USUARIO = "student"
CONTRASENA = "Password123"

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 10)

print(f"Navegando a: {URL}")
driver.get(URL)

# ---- LOGIN EXITOSO ----
print("\n--- Prueba 1: Login exitoso ---")

# Encontrar y llenar campo usuario
campo_usuario = driver.find_element(By.ID, "username")
campo_usuario.clear()
campo_usuario.send_keys(USUARIO)
print(f"Usuario ingresado: {USUARIO}")

# Encontrar y llenar campo contrasena
campo_pass = driver.find_element(By.ID, "password")
campo_pass.clear()
campo_pass.send_keys(CONTRASENA)
print("Contrasena ingresada")

# Hacer click en el boton de login
boton_login = driver.find_element(By.ID, "submit")
boton_login.click()
print("Boton de login presionado")

# Esperar a que cargue la pagina de exito
wait.until(EC.url_contains("logged-in-successfully"))

# Verificar el mensaje de exito
titulo = driver.find_element(By.TAG_NAME, "h1").text
print(f"Titulo de la pagina: '{titulo}'")

if "Congratulations" in titulo:
    print("RESULTADO: LOGIN EXITOSO - Test PASADO")
else:
    print("RESULTADO: ALGO SALIO MAL - Test FALLIDO")

# Guardar screenshot como evidencia
driver.save_screenshot("evidencia_login_exitoso.png")
print("Screenshot guardado: evidencia_login_exitoso.png")

# Volver al login para la segunda prueba
driver.back()

# ---- LOGIN FALLIDO ----
print("\n--- Prueba 2: Login fallido (credenciales incorrectas) ---")

campo_usuario = wait.until(EC.presence_of_element_located((By.ID, "username")))
campo_usuario.clear()
campo_usuario.send_keys("usuario_incorrecto")

campo_pass = driver.find_element(By.ID, "password")
campo_pass.clear()
campo_pass.send_keys("contrasena_incorrecta")

driver.find_element(By.ID, "submit").click()

# Esperar el mensaje de error
error = wait.until(EC.visibility_of_element_located((By.ID, "error")))
print(f"Mensaje de error: '{error.text}'")

if "invalid" in error.text.lower():
    print("RESULTADO: Error detectado correctamente - Test PASADO")
else:
    print("RESULTADO: No se detecto el error esperado - Test FALLIDO")

driver.save_screenshot("evidencia_login_fallido.png")
print("Screenshot guardado: evidencia_login_fallido.png")

driver.quit()
print("\nEjercicio 4 completado!")
