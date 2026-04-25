# Guia del Instructor - Curso Selenium con Python

## Estructura del curso

```
selenium-curso/
├── CURSO_SELENIUM_SLIDES.md     <- Tu PPT (convertir con tu herramienta preferida)
├── INSTRUCTOR_README.md         <- Esta guia
└── ejercicios/
    ├── 01_hola_mundo.py
    ├── 02_encontrar_elementos.py
    ├── 03_busqueda_google.py
    ├── 04_login_automatico.py
    ├── 05_esperas_explicitas.py
    └── 06_proyecto_final_saucedemo.py
```

---

## Antes de la clase

### Instalar todo esto tu mismo primero:
```bash
pip install selenium webdriver-manager pytest
```

### Correr cada script y verificar que funciona:
```bash
python ejercicios/01_hola_mundo.py
python ejercicios/02_encontrar_elementos.py
python ejercicios/03_busqueda_google.py
python ejercicios/04_login_automatico.py
python ejercicios/05_esperas_explicitas.py
pytest ejercicios/06_proyecto_final_saucedemo.py -v
```

### Sitios que deben funcionar sin cuenta:
- google.com (siempre funciona)
- practicetestautomation.com/practice-test-login/ (usuario: student / Password123)
- saucedemo.com (usuario: standard_user / secret_sauce)

---

## Estructura del dia (3.5-4 horas)

| Tiempo | Bloque | Contenido |
|--------|--------|-----------|
| 0:00 - 0:20 | Intro | Que es Selenium, para que sirve |
| 0:20 - 0:45 | Instalacion | Setup del entorno, primer script |
| 0:45 - 1:00 | BREAK | Descanso 15 min |
| 1:00 - 1:35 | Locators | find_element, DevTools, XPath |
| 1:35 - 2:05 | Interacciones | click, send_keys, Select, esperas |
| 2:05 - 2:15 | BREAK | Descanso 10 min |
| 2:15 - 2:40 | Testing | pytest, assertions, screenshots |
| 2:40 - 3:30 | Proyecto Final | SauceDemo test suite |
| 3:30 - 3:45 | Cierre | Recursos, preguntas, que sigue |

---

## Tips para dar la clase

1. **Siempre codea en vivo** — no solo muestres el codigo, escribelo en pantalla
2. **Rompe las cosas a proposito** — mostrar errores y como debuggearlos es muy valioso
3. **Usa DevTools en vivo** — abre Inspect Element y muestra como encontrar IDs y nombres
4. **Para si alguien se queda atras** — es mejor ir lento que dejar gente perdida
5. **Los breaks son importantes** — la gente necesita procesar

---

## Como convertir el MD a PPT

### Opcion 1: Marp (recomendado, gratis)
```bash
npm install -g @marp-team/marp-cli
marp CURSO_SELENIUM_SLIDES.md --pptx
```

### Opcion 2: Copiar y pegar en PowerPoint
- Cada seccion `## Diapositiva N` es una diapositiva
- Copiar el contenido de cada una en una slide de PowerPoint

### Opcion 3: Google Slides
- Importar el MD o copiar el contenido manualmente

---

## Preguntas frecuentes que te van a hacer

**"Que diferencia hay entre Selenium y Playwright?"**
> Playwright es mas moderno (2020), mas rapido, y tiene mejor soporte async. Selenium es mas maduro (2004), tiene mas documentacion, mas usado en empresas grandes. Para aprender automation, ambos sirven. Para trabajo, Selenium tiene mas demanda laboral hoy en dia.

**"Puedo usar Selenium con Firefox?"**
> Si: `webdriver.Firefox()` con `geckodriver`. La sintaxis es identica.

**"Como hago para que corra sin que se abra el navegador?"**
> Modo headless: agrega `options.add_argument("--headless")` al crear el driver. Util para servidores CI/CD.

**"Que es CI/CD y como corre Selenium ahi?"**
> Es automatizacion de despliegue. Los tests corren en modo headless en cada pull request. Herramientas: GitHub Actions, Jenkins, GitLab CI.

**"Cuanto se gana siendo QA Automation?"**
> En Mexico/Latinoamerica: $25,000-$60,000 MXN/mes. En USA remoto: $60,000-$120,000 USD/ano.
