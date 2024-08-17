from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
from shutil import which

def iniciar_webdriver(headless=True):
    """arrnca webdriver y lo devuelve"""
    options = Options()
    if headless:
        options.add_argument("--headless")  # para que no se abra la ventana de chrome
    options.add_argument("--window-size=1920, 1080")
    options.add_argument("--start-maximized")  # iniciamos meximizada la ventana
    options.add_argument("--disable-dev-shm-usage")  # para usar directorio temporal para crear archivos anonimos de memoria compartida
    options.add_argument("--disable-blink-features=AutomationControlled")  # para que navigator.webdriver sea Falsex
    options.add_argument("--log-level=3")  # para que no muestre nada en la terminal
    lista = [
        'enable-automation' #para ocultar software automatizado de pruebas
        'enable-logging'  # para ocultar Devtools...
    ]
    options.add_experimental_option('excludeSwitches', lista)
    s = Service(which("chromedriver"))
    driver = webdriver.Chrome(service=s, options=option)
    stealth(
        driver,
        languages=["es-ES", "es"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGl Engine",
        fix_hairline=True,
    )
    return driver

# print("hello world")