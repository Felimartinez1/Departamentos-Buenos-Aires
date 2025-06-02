import tempfile
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

def preload_driver_binary():
    """
    Precarga el binario de undetected_chromedriver (Zonaprop) para que
    los procesos hijos no lo descarguen/parcheen simultáneamente.
    """
    driver = uc.Chrome(use_subprocess=False)
    driver.quit()

def create_browser_zona(headless: bool = False):
    """
    Crea una instancia de undetected_chromedriver para ZonaProp,
    con user-data-dir distinto y soporte multi procesos.
    """
    tmp_profile = tempfile.mkdtemp(prefix="uc_profile_")
    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={tmp_profile}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    if headless:
        # En Chrome 109+ se puede usar "--headless=new", pero omitimos "new" por compatibilidad
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")

    return uc.Chrome(
        options=options,
        use_subprocess=False,
        user_multi_procs=True
    )

def create_browser_remax(headless: bool = True, driver_path: str = None):
    """
    Crea una instancia de Selenium Chrome para REMAX.
    Si driver_path está provisto, se fuerza a usar ese ejecutable.
    """
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--enable-unsafe-swiftshader")

    if driver_path:
        service = Service(executable_path=driver_path, use_selenium_manager=False)
        return webdriver.Chrome(service=service, options=options)
    else:
        return webdriver.Chrome(options=options)
