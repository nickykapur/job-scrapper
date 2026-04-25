# Introduccion a Selenium con Python
### Curso Practico de Automatizacion y Testing Web
**Duracion estimada: 3-4 horas**
**Nivel: Principiante**

---

## GUIA DEL INSTRUCTOR

> Este documento es tu guia completa para dar la clase. Cada seccion tiene:
> - Lo que debes decir (en cursiva)
> - Lo que debes mostrar en pantalla
> - Los ejercicios que el alumno hace
> - Preguntas frecuentes y como responderlas

---

---

# BLOQUE 1: INTRODUCCION Y CONTEXTO
## ~20 minutos | 5 diapositivas

---

## Diapositiva 1 — Portada

**Titulo:** Selenium con Python: Automatizacion y Testing Web

**Subtitulo:** Aprende a hacer que el navegador trabaje por ti

**Imagen sugerida:** Captura de un navegador con codigo Python al lado

**Lo que dices:**
> *"Bienvenidos. Hoy vamos a aprender una herramienta que usan empresas como Google, Amazon y Netflix para probar sus sitios web antes de publicar cambios. Se llama Selenium. Al final de esta clase, cada uno va a poder escribir un script que abre un navegador, navega a una pagina y ejecuta acciones automaticamente. Sin tocar el mouse."*

---

## Diapositiva 2 — El Problema: Las Pruebas Manuales

**Titulo:** El problema con las pruebas manuales

**Contenido (bullets):**
- Tienes un sitio web con 50 formularios
- Cada vez que cambias algo, alguien tiene que probar los 50
- Eso tarda horas... o dias
- Los humanos se equivocan, se cansan, se aburren
- Y encima, el cliente quiere el fix en 2 horas

**Imagen sugerida:** Persona frustrada frente a computadora

**Lo que dices:**
> *"Imaginen que trabajan en una empresa y su jefe les dice: 'Cambiamos el sistema de login, prueben que todo funcione'. ¿Cuanto tiempo les tomaria probar el login, el registro, el formulario de contacto, el carrito de compras...? Selenium resuelve exactamente eso."*

---

## Diapositiva 3 — La Solucion: Selenium

**Titulo:** Que es Selenium?

**Contenido:**
- Herramienta de automatizacion de navegadores web
- Open source y gratuita (creada en 2004, mantenida por la comunidad)
- Soporta: Chrome, Firefox, Edge, Safari
- Soporta: Python, Java, JavaScript, C#, Ruby
- Usada por: Netflix, Google, Amazon, y miles de empresas

**Analogia clave para decir en voz alta:**
> *"Selenium es como un 'robot fantasma' que controla el navegador. El robot puede hacer todo lo que tu haces: abrir paginas, hacer clic, escribir texto, llenar formularios. Pero lo hace en milisegundos y sin cansarse."*

---

## Diapositiva 4 — Para que se usa?

**Titulo:** Casos de uso reales

**Tabla en la diapositiva:**

| Caso de uso | Ejemplo real |
|---|---|
| Testing de regresion | Probar que un fix no rompio nada mas |
| Pruebas de formularios | Verificar validaciones de login/registro |
| Scraping de datos | Extraer precios, noticias, empleos |
| Automatizacion de tareas | Llenar formularios repetitivos |
| Pruebas de compatibilidad | Probar en Chrome Y Firefox a la vez |

**Lo que dices:**
> *"No solo sirve para testing. Muchas empresas usan Selenium para extraer datos de sitios web o automatizar tareas aburridas. Pero hoy nos enfocamos en testing."*

---

## Diapositiva 5 — Lo que van a poder hacer hoy

**Titulo:** Al terminar esta clase vas a poder...

**Bullets:**
- Instalar y configurar Selenium en Python
- Abrir un navegador con codigo
- Navegar a cualquier URL
- Encontrar elementos en la pagina (botones, campos, links)
- Hacer clic, escribir texto, y enviar formularios
- Verificar que la pagina muestre lo que debe mostrar
- Escribir tu primer test automatizado completo

**Lo que dices:**
> *"Esto no es teoria. Cada concepto lo vamos a practicar inmediatamente con codigo real. Tienen que tener su computadora lista porque vamos a codear juntos."*

---

---

# BLOQUE 2: INSTALACION Y CONFIGURACION
## ~25 minutos | 4 diapositivas

---

## Diapositiva 6 — Que necesitamos instalar

**Titulo:** Configuracion del entorno

**Lista de requisitos:**
1. Python 3.8+ (verificar con `python --version`)
2. pip (viene con Python)
3. Selenium (`pip install selenium`)
4. Chrome browser (ya lo tienen)
5. ChromeDriver (lo maneja Selenium automaticamente desde v4.6+)

**Nota para el instructor:**
> Si alguien tiene Python 2.x o no tiene Python, dirigirlos a python.org. Tardan 5 minutos en instalar.

---

## Diapositiva 7 — Instalacion en vivo

**Titulo:** Instalamos juntos

**Comandos a mostrar en pantalla (uno por uno):**

```bash
# 1. Verificar Python
python --version

# 2. Instalar Selenium
pip install selenium

# 3. Instalar webdriver-manager (facilita la gestion de drivers)
pip install webdriver-manager

# 4. Verificar instalacion
python -c "import selenium; print(selenium.__version__)"
```

**Lo que dices mientras instalan:**
> *"Selenium version 4 en adelante maneja ChromeDriver automaticamente. No tienen que descargar nada extra. Antes habia que hacerlo manualmente y era un dolor de cabeza, pero ya no."*

**Problema frecuente:**
> Si `pip` no funciona, probar `pip3` o `python -m pip install selenium`

---

## Diapositiva 8 — Estructura del proyecto

**Titulo:** Como organizamos nuestros archivos

**Estructura de carpetas a mostrar:**
```
mi-proyecto-selenium/
│
├── tests/
│   ├── test_login.py
│   ├── test_busqueda.py
│   └── test_formulario.py
│
├── pages/
│   └── (avanzado - Page Objects, lo veremos al final)
│
└── requirements.txt
```

**Lo que dices:**
> *"Para esta clase vamos a trabajar en archivos simples. No se preocupen por la carpeta 'pages', eso es un patron avanzado que mencionaremos al final."*

---

## Diapositiva 9 — Primer script: Hola Mundo de Selenium

**Titulo:** Tu primer script de Selenium

**Codigo a mostrar Y escribir en vivo:**
```python
# primer_script.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Crear el navegador
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Abrir una pagina
driver.get("https://www.google.com")

# Esperar 3 segundos para verlo
import time
time.sleep(3)

# Cerrar el navegador
driver.quit()

print("Script completado!")
```

**Lo que dices antes de ejecutar:**
> *"Van a ver que se abre Chrome solo. No toquen nada. El script lo controla."*

**Ejercicio 1 (5 min):**
> Cambiar `google.com` por cualquier sitio que quieran. Ejecutar. Ver que pasa.

---

---

# BLOQUE 3: ENCONTRAR ELEMENTOS EN LA PAGINA
## ~35 minutos | 6 diapositivas

---

## Diapositiva 10 — El concepto mas importante: Locators

**Titulo:** Como Selenium "ve" la pagina

**Explicacion visual:**
> Una pagina web es como un arbol de bloques. Selenium puede encontrar cualquier bloque si sabes como buscarlo.

**Los 5 locators principales:**

| Metodo | Que busca | Ejemplo |
|---|---|---|
| `By.ID` | Atributo id="..." | `id="username"` |
| `By.NAME` | Atributo name="..." | `name="email"` |
| `By.CLASS_NAME` | Clase CSS | `class="btn-primary"` |
| `By.XPATH` | Ruta completa al elemento | (lo vemos despues) |
| `By.CSS_SELECTOR` | Selector CSS | `#form > input` |

**Lo que dices:**
> *"El mas facil de entender es By.ID. Si un elemento tiene un ID unico en la pagina, es la forma mas rapida y confiable de encontrarlo. Siempre busquen primero si hay un ID."*

---

## Diapositiva 11 — Como ver el HTML: DevTools

**Titulo:** La herramienta secreta: Inspect Element

**Pasos a mostrar en vivo:**
1. Abrir Chrome
2. Ir a cualquier pagina (ej: google.com)
3. Click derecho sobre el campo de busqueda
4. Seleccionar "Inspect" / "Inspeccionar"
5. Ver el HTML resaltado
6. Buscar el atributo `id`, `name`, o `class`

**Lo que dices:**
> *"Este es el truco que usan todos los que trabajan con Selenium. Antes de escribir codigo, siempre inspeccionen el elemento para saber como encontrarlo. Es como el mapa antes de ir al destino."*

**Ejercicio 2 (5 min):**
> Ir a google.com, inspeccionar el campo de busqueda, encontrar el `name` o `id`. (Respuesta: `name="q"`)

---

## Diapositiva 12 — find_element en accion

**Titulo:** Encontrando elementos con codigo

**Codigo:**
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://www.google.com")

# Encontrar el campo de busqueda por su atributo 'name'
campo_busqueda = driver.find_element(By.NAME, "q")

# Escribir en el campo
campo_busqueda.send_keys("Selenium Python tutorial")

# Presionar Enter
from selenium.webdriver.common.keys import Keys
campo_busqueda.send_keys(Keys.RETURN)

import time
time.sleep(3)
driver.quit()
```

**Lo que dices:**
> *"Noten que primero 'encontramos' el elemento y lo guardamos en una variable. Luego le decimos que hacer. Es siempre en dos pasos: encontrar, luego actuar."*

---

## Diapositiva 13 — XPath: el locator todopoderoso

**Titulo:** XPath: cuando nada mas funciona

**Cuando usar XPath:**
- El elemento no tiene ID ni name
- La clase CSS es dinamica (cambia cada vez)
- Necesitas buscar por texto visible

**Ejemplos de XPath comunes:**
```python
# Por texto visible
driver.find_element(By.XPATH, "//button[text()='Iniciar sesion']")

# Por atributo cualquiera
driver.find_element(By.XPATH, "//input[@placeholder='Buscar...']")

# Elemento hijo especifico
driver.find_element(By.XPATH, "//form[@id='login']/input[1]")
```

**Truco para generar XPath automaticamente:**
> DevTools → Click derecho en el elemento → Copy → Copy XPath

**Lo que dices:**
> *"XPath es como GPS. Puede llegar a cualquier elemento de la pagina. Es mas fragil que ID porque si cambia el HTML puede romperse, pero cuando no hay otra opcion, XPath es tu mejor amigo."*

---

## Diapositiva 14 — find_element vs find_elements

**Titulo:** Uno vs Muchos

**Diferencia clave:**

```python
# find_element → devuelve UN elemento (el primero que encuentra)
# Si no lo encuentra → lanza excepcion NoSuchElementException
boton = driver.find_element(By.CLASS_NAME, "btn-primary")

# find_elements → devuelve una LISTA (puede estar vacia)
# Si no encuentra nada → devuelve lista vacia []
todos_los_links = driver.find_elements(By.TAG_NAME, "a")
print(f"Hay {len(todos_los_links)} links en esta pagina")
```

**Lo que dices:**
> *"Esta es una diferencia que causa muchos bugs. find_element singular falla si no encuentra nada. find_elements plural nunca falla, solo devuelve una lista vacia. Usen el plural cuando no esten seguros si el elemento existe."*

---

## Diapositiva 15 — Ejercicio Practico: Busqueda en Google

**Titulo:** Ejercicio 3 — Automatizar una busqueda

**Enunciado para los alumnos:**
> Escribe un script que:
> 1. Abra Google
> 2. Busque "noticias de hoy"
> 3. Espere 2 segundos
> 4. Cuente cuantos resultados hay en la pagina
> 5. Imprima el titulo de cada resultado

**Pista:**
```python
# Los resultados de Google tienen la clase "LC20lb MBeuO DKV0Md" 
# o usar: By.XPATH, "//h3"
resultados = driver.find_elements(By.TAG_NAME, "h3")
for r in resultados:
    print(r.text)
```

**Tiempo: 10 minutos**

---

---

# BLOQUE 4: INTERACCIONES Y ACCIONES
## ~30 minutos | 5 diapositivas

---

## Diapositiva 16 — Acciones disponibles en elementos

**Titulo:** Que podemos hacer con un elemento?

**Tabla de acciones:**

| Accion | Metodo | Cuando se usa |
|---|---|---|
| Hacer clic | `.click()` | Botones, links, checkboxes |
| Escribir texto | `.send_keys("texto")` | Inputs, textareas |
| Borrar texto | `.clear()` | Antes de escribir nuevo texto |
| Obtener texto | `.text` | Leer lo que muestra el elemento |
| Obtener atributo | `.get_attribute("href")` | Leer href, value, class, etc |
| Verificar si es visible | `.is_displayed()` | Checar si el elemento esta visible |
| Verificar si es clickeable | `.is_enabled()` | Checar si no esta deshabilitado |

---

## Diapositiva 17 — Selectores Dropdown

**Titulo:** Trabajando con listas desplegables

**Codigo:**
```python
from selenium.webdriver.support.ui import Select

# Encontrar el elemento select
dropdown = driver.find_element(By.ID, "pais")
select = Select(dropdown)

# Tres formas de seleccionar una opcion:
select.select_by_visible_text("Mexico")   # Por texto visible
select.select_by_value("MX")              # Por valor del option
select.select_by_index(5)                 # Por posicion (0-based)

# Obtener la opcion seleccionada actualmente
opcion_actual = select.first_selected_option
print(opcion_actual.text)
```

---

## Diapositiva 18 — Esperas: el tema mas importante

**Titulo:** El error mas comun: No esperar

**El problema:**
```python
# MALO - puede fallar si la pagina es lenta
driver.get("https://sitio-lento.com")
boton = driver.find_element(By.ID, "boton-que-carga-tarde")
# ERROR: NoSuchElementException - el elemento no ha cargado aun!
```

**Las tres formas de esperar:**

```python
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 1. Espera fija (MALA PRACTICA - lenta y fragil)
time.sleep(3)

# 2. Espera implicita (mejor, pero limitada)
driver.implicitly_wait(10)  # espera hasta 10 segundos en cualquier find_element

# 3. Espera explicita (LA MEJOR - espera exactamente lo que necesitas)
wait = WebDriverWait(driver, 10)
elemento = wait.until(
    EC.presence_of_element_located((By.ID, "mi-elemento"))
)
```

**Lo que dices:**
> *"Este es el tema que mas problemas causa a los principiantes. El navegador a veces es mas rapido que la pagina. Selenium intenta encontrar el elemento antes de que cargue y falla. Las esperas explicitas resuelven esto."*

---

## Diapositiva 19 — Esperas Explicitas: mas ejemplos

**Titulo:** Condiciones de espera mas usadas

```python
from selenium.webdriver.support import expected_conditions as EC

wait = WebDriverWait(driver, 10)

# Esperar a que el elemento exista en el DOM
wait.until(EC.presence_of_element_located((By.ID, "resultado")))

# Esperar a que el elemento sea visible
wait.until(EC.visibility_of_element_located((By.ID, "modal")))

# Esperar a que el elemento sea clickeable
wait.until(EC.element_to_be_clickable((By.ID, "btn-submit")))

# Esperar a que el texto aparezca en la pagina
wait.until(EC.text_to_be_present_in_element((By.ID, "status"), "Completado"))

# Esperar a que el URL cambie
wait.until(EC.url_contains("dashboard"))
```

---

## Diapositiva 20 — Ejercicio: Login Automatizado

**Titulo:** Ejercicio 4 — Automatizar un Login

**Usaremos este sitio de practica:** `https://practicetestautomation.com/practice-test-login/`

**Enunciado:**
> Escribe un script que:
> 1. Abra el sitio de practica
> 2. Escriba el usuario: `student`
> 3. Escriba la contrasena: `Password123`
> 4. Haga clic en el boton de login
> 5. Verifique que aparece el texto "Congratulations"

**Tiempo: 10 minutos**

---

---

# BLOQUE 5: TESTING Y ASSERTIONS
## ~25 minutos | 4 diapositivas

---

## Diapositiva 21 — Que es un "Test"?

**Titulo:** De script a test real

**Diferencia:**
```python
# SCRIPT: hace cosas
driver.find_element(By.ID, "resultado").text

# TEST: hace cosas Y verifica que sean correctas
texto = driver.find_element(By.ID, "resultado").text
assert texto == "Login exitoso", f"Se esperaba 'Login exitoso' pero se obtuvo: '{texto}'"
```

**Lo que dices:**
> *"Un script automatiza. Un test automatiza Y verifica. La diferencia es el 'assert'. Si la condicion no se cumple, el test falla y nos avisa. Eso es exactamente lo que queremos: que el programa nos diga si algo esta mal."*

---

## Diapositiva 22 — Usando pytest con Selenium

**Titulo:** pytest: el framework de testing de Python

**Instalacion:**
```bash
pip install pytest
```

**Estructura de un test con pytest:**
```python
# test_login.py
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class TestLogin:
    
    def setup_method(self):
        """Se ejecuta ANTES de cada test"""
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install())
        )
        self.driver.get("https://practicetestautomation.com/practice-test-login/")
    
    def teardown_method(self):
        """Se ejecuta DESPUES de cada test"""
        self.driver.quit()
    
    def test_login_exitoso(self):
        self.driver.find_element(By.ID, "username").send_keys("student")
        self.driver.find_element(By.ID, "password").send_keys("Password123")
        self.driver.find_element(By.ID, "submit").click()
        
        mensaje = self.driver.find_element(By.TAG_NAME, "h1").text
        assert "Congratulations" in mensaje
    
    def test_login_fallido(self):
        self.driver.find_element(By.ID, "username").send_keys("usuario_malo")
        self.driver.find_element(By.ID, "password").send_keys("contrasena_mala")
        self.driver.find_element(By.ID, "submit").click()
        
        error = self.driver.find_element(By.ID, "error").text
        assert "Your username is invalid!" in error
```

**Ejecutar:**
```bash
pytest test_login.py -v
```

---

## Diapositiva 23 — Assertions mas usados

**Titulo:** Que podemos verificar?

```python
# Texto exacto
assert elemento.text == "Bienvenido"

# Texto contenido
assert "exitoso" in elemento.text.lower()

# URL actual
assert "dashboard" in driver.current_url

# Titulo de la pagina
assert driver.title == "Mi Sitio Web"

# Elemento visible
assert elemento.is_displayed()

# Elemento habilitado (no disabled)
assert boton.is_enabled()

# Cantidad de elementos
resultados = driver.find_elements(By.CLASS_NAME, "producto")
assert len(resultados) > 0, "No se encontraron productos"
assert len(resultados) == 10, f"Se esperaban 10 resultados, hay {len(resultados)}"
```

---

## Diapositiva 24 — Screenshots para evidencia

**Titulo:** Guardar evidencia de los tests

```python
# Screenshot de toda la pagina
driver.save_screenshot("evidencia_test.png")

# Screenshot de un elemento especifico
elemento = driver.find_element(By.ID, "resultado")
elemento.screenshot("evidencia_elemento.png")

# Screenshot cuando falla un test (muy util)
def test_con_screenshot_en_fallo(self):
    try:
        resultado = self.driver.find_element(By.ID, "mensaje").text
        assert resultado == "Exito"
    except AssertionError:
        self.driver.save_screenshot("fallo_test.png")
        raise  # Re-lanzar el error para que pytest lo marque como fallido
```

**Lo que dices:**
> *"En equipos reales, los screenshots son la evidencia de que el test corrio. Los QA los guardan en reportes. Hay herramientas como Allure Report que los incluyen automaticamente, pero eso es tema avanzado."*

---

---

# BLOQUE 6: PROYECTO FINAL Y CIERRE
## ~30 minutos | 4 diapositivas

---

## Diapositiva 25 — Proyecto Final

**Titulo:** Proyecto Final — Test Suite Completo

**Sitio de practica:** `https://www.saucedemo.com`
- Usuario: `standard_user`
- Contrasena: `secret_sauce`

**Tests a escribir:**

```
Test 1: Login exitoso
- Abrir el sitio
- Ingresar credenciales correctas
- Verificar que llega al inventario (URL contiene "inventory")

Test 2: Login fallido
- Intentar login con credenciales incorrectas
- Verificar que aparece mensaje de error

Test 3: Agregar producto al carrito
- Hacer login
- Agregar el primer producto al carrito
- Verificar que el contador del carrito muestra "1"

Test 4: Completar una compra
- Hacer login
- Agregar producto
- Ir al carrito
- Hacer checkout
- Llenar formulario (nombre, apellido, codigo postal)
- Verificar que la orden fue completada
```

**Tiempo: 20 minutos**

---

## Diapositiva 26 — Buenas Practicas

**Titulo:** Lo que hacen los profesionales

**Lista:**
1. **Un test, una cosa** — cada test verifica solo un comportamiento
2. **Tests independientes** — cada test puede correr solo, sin depender de otro
3. **Nombres descriptivos** — `test_login_con_usuario_bloqueado` no `test_3`
4. **No usar `time.sleep()`** — usar esperas explicitas (WebDriverWait)
5. **Page Object Model** — separar la logica de la pagina del test (avanzado)
6. **Datos de prueba separados** — no hardcodear usuario/contrasena en el test

---

## Diapositiva 27 — Que sigue? Recursos

**Titulo:** Para seguir aprendiendo

**Recursos:**
- Documentacion oficial: selenium.dev/documentation
- Sitios de practica gratis:
  - practicetestautomation.com
  - saucedemo.com
  - the-internet.herokuapp.com
  - automationexercise.com

**Temas avanzados para explorar:**
- Page Object Model (POM)
- pytest fixtures y conftest.py
- Selenium Grid (correr tests en paralelo)
- Allure Report (reportes bonitos)
- CI/CD con GitHub Actions
- Playwright (alternativa moderna a Selenium)

---

## Diapositiva 28 — Resumen y Preguntas

**Titulo:** Lo que aprendimos hoy

**Resumen:**
- Que es Selenium y para que sirve
- Como instalar y configurar el entorno
- Como encontrar elementos (By.ID, By.NAME, By.XPATH, By.CSS_SELECTOR)
- Como interactuar (click, send_keys, clear, select)
- Por que las esperas son importantes (WebDriverWait)
- Como escribir tests reales con pytest y assertions
- Como guardar screenshots como evidencia

**Mensaje final para decir:**
> *"Selenium es una habilidad muy valorada en el mercado. Un QA Automation Engineer con Python puede ganar entre $60,000 y $120,000 al ano en Estados Unidos. Y lo que aprendieron hoy es la base de todo eso. El siguiente paso es practicar todos los dias, aunque sea 30 minutos."*

---

---

# APENDICE: GUIA DE PROBLEMAS COMUNES

## Errores frecuentes y como resolverlos

| Error | Causa | Solucion |
|---|---|---|
| `NoSuchElementException` | El elemento no existe o no ha cargado | Usar WebDriverWait, verificar el locator con DevTools |
| `ElementClickInterceptedException` | Otro elemento cubre el que quieren clickear | Usar JavaScript click o hacer scroll primero |
| `StaleElementReferenceException` | La pagina se recargo y el elemento ya no es el mismo | Volver a hacer find_element |
| `TimeoutException` | El elemento no aparecio en el tiempo dado | Aumentar el timeout, verificar que el elemento existe |
| `WebDriverException` | ChromeDriver no encontrado o version incompatible | Usar webdriver-manager para manejo automatico |

---

## Comandos rapidos de referencia

```bash
# Instalar todo
pip install selenium webdriver-manager pytest

# Ejecutar todos los tests
pytest tests/ -v

# Ejecutar un test especifico
pytest tests/test_login.py::TestLogin::test_login_exitoso -v

# Ejecutar con reporte detallado
pytest tests/ -v --tb=short

# Ver version de selenium
python -c "import selenium; print(selenium.__version__)"
```
