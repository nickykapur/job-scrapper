"""
PROYECTO FINAL: Suite de Tests para SauceDemo
==============================================
Sitio: https://www.saucedemo.com
Usuario: standard_user
Contrasena: secret_sauce

Este archivo contiene 4 tests completos usando pytest.
Ejecutar con: pytest 06_proyecto_final_saucedemo.py -v

Conceptos cubiertos:
- setup_method y teardown_method
- Tests independientes
- Assertions con mensajes de error
- Screenshots en fallos
- Test suite completo
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

URL = "https://www.saucedemo.com"
USUARIO = "standard_user"
CONTRASENA = "secret_sauce"


class TestSauceDemo:
    """Suite de tests para el sitio de practica SauceDemo"""

    def setup_method(self):
        """Se ejecuta ANTES de cada test - crea un navegador limpio"""
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install())
        )
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 10)
        self.driver.get(URL)

    def teardown_method(self):
        """Se ejecuta DESPUES de cada test - cierra el navegador"""
        self.driver.quit()

    def _hacer_login(self):
        """Metodo auxiliar para hacer login (reutilizado en varios tests)"""
        self.driver.find_element(By.ID, "user-name").send_keys(USUARIO)
        self.driver.find_element(By.ID, "password").send_keys(CONTRASENA)
        self.driver.find_element(By.ID, "login-button").click()
        self.wait.until(EC.url_contains("inventory"))

    # ================================================================
    # TEST 1: Login exitoso
    # ================================================================
    def test_login_exitoso(self):
        """Verifica que el login con credenciales correctas funciona"""
        # Llenar el formulario
        self.driver.find_element(By.ID, "user-name").send_keys(USUARIO)
        self.driver.find_element(By.ID, "password").send_keys(CONTRASENA)
        self.driver.find_element(By.ID, "login-button").click()

        # Verificar que llegamos al inventario
        self.wait.until(EC.url_contains("inventory"))
        assert "inventory" in self.driver.current_url, \
            f"Deberia estar en inventory, URL actual: {self.driver.current_url}"

        # Verificar titulo de la pagina de productos
        titulo = self.driver.find_element(By.CLASS_NAME, "title").text
        assert titulo == "Products", \
            f"Se esperaba titulo 'Products', se obtuvo '{titulo}'"

        print("Test 1 PASADO: Login exitoso")

    # ================================================================
    # TEST 2: Login fallido
    # ================================================================
    def test_login_fallido(self):
        """Verifica que el login con credenciales incorrectas muestra error"""
        self.driver.find_element(By.ID, "user-name").send_keys("usuario_malo")
        self.driver.find_element(By.ID, "password").send_keys("contrasena_mala")
        self.driver.find_element(By.ID, "login-button").click()

        # Esperar el mensaje de error
        error = self.wait.until(
            EC.visibility_of_element_located((By.CLASS_NAME, "error-message-container"))
        )

        assert error.is_displayed(), "El mensaje de error deberia ser visible"
        assert "Epic sadface" in error.text, \
            f"Mensaje de error inesperado: '{error.text}'"

        # Verificar que NO navegamos al inventario
        assert "inventory" not in self.driver.current_url, \
            "No deberia haberse navegado al inventario con credenciales incorrectas"

        print("Test 2 PASADO: Error de login detectado correctamente")

    # ================================================================
    # TEST 3: Agregar producto al carrito
    # ================================================================
    def test_agregar_producto_al_carrito(self):
        """Verifica que se puede agregar un producto al carrito"""
        self._hacer_login()

        # Verificar que hay productos
        productos = self.driver.find_elements(By.CLASS_NAME, "inventory-item")
        assert len(productos) > 0, "Deberia haber productos en el inventario"
        print(f"Productos disponibles: {len(productos)}")

        # Agregar el primer producto
        primer_boton_agregar = self.driver.find_element(
            By.XPATH, "//button[contains(text(), 'Add to cart')]"
        )
        nombre_producto = self.driver.find_element(
            By.CLASS_NAME, "inventory-item-name"
        ).text
        primer_boton_agregar.click()
        print(f"Producto agregado: '{nombre_producto}'")

        # Verificar el contador del carrito
        contador_carrito = self.driver.find_element(
            By.CLASS_NAME, "shopping_cart_badge"
        )
        assert contador_carrito.text == "1", \
            f"El carrito deberia tener 1 item, tiene: '{contador_carrito.text}'"

        print("Test 3 PASADO: Producto agregado al carrito correctamente")

    # ================================================================
    # TEST 4: Completar una compra
    # ================================================================
    def test_completar_compra(self):
        """Verifica el flujo completo de compra"""
        self._hacer_login()

        # Agregar primer producto
        self.driver.find_element(
            By.XPATH, "//button[contains(text(), 'Add to cart')]"
        ).click()

        # Ir al carrito
        self.driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
        self.wait.until(EC.url_contains("cart"))
        assert "cart" in self.driver.current_url

        # Proceder al checkout
        self.driver.find_element(By.ID, "checkout").click()
        self.wait.until(EC.url_contains("checkout-step-one"))

        # Llenar informacion de envio
        self.driver.find_element(By.ID, "first-name").send_keys("Juan")
        self.driver.find_element(By.ID, "last-name").send_keys("Perez")
        self.driver.find_element(By.ID, "postal-code").send_keys("12345")

        # Continuar
        self.driver.find_element(By.ID, "continue").click()
        self.wait.until(EC.url_contains("checkout-step-two"))

        # Confirmar orden
        self.driver.find_element(By.ID, "finish").click()
        self.wait.until(EC.url_contains("checkout-complete"))

        # Verificar mensaje de exito
        mensaje = self.driver.find_element(By.CLASS_NAME, "complete-header").text
        assert "Thank you" in mensaje, \
            f"Se esperaba mensaje de agradecimiento, se obtuvo: '{mensaje}'"

        print(f"Mensaje de confirmacion: '{mensaje}'")
        self.driver.save_screenshot("compra_completada.png")
        print("Test 4 PASADO: Compra completada exitosamente")


# ================================================================
# Para ejecutar estos tests:
# pytest 06_proyecto_final_saucedemo.py -v
#
# Para ejecutar un test especifico:
# pytest 06_proyecto_final_saucedemo.py::TestSauceDemo::test_login_exitoso -v
# ================================================================
