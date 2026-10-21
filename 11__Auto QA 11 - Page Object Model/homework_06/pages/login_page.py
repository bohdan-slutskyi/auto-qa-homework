"""Page Object страницы авторизации SauceDemo."""

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class LoginPage:
    """Операции со страницей входа в SauceDemo."""

    URL = "https://www.saucedemo.com/"
    USERNAME_INPUT = (By.ID, "user-name")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")

    def __init__(self, driver: WebDriver, timeout: int = 15) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open(self) -> None:
        """Открывает страницу авторизации."""
        self.driver.get(self.URL)

    def login(self, username: str, password: str) -> None:
        """Выполняет вход с переданными учётными данными."""
        username_field = self.wait.until(
            EC.visibility_of_element_located(self.USERNAME_INPUT)
        )
        username_field.send_keys(username)

        password_field = self.wait.until(
            EC.visibility_of_element_located(self.PASSWORD_INPUT)
        )
        password_field.send_keys(password)

        self._click_and_wait_for_url(self.LOGIN_BUTTON, "/inventory.html")

    def _click_and_wait_for_url(
        self,
        locator: tuple[str, str],
        url_part: str,
    ) -> None:
        """Повторяет native click до подтверждения перехода маршрута."""

        def click_and_check_url(driver: WebDriver) -> bool:
            if url_part in driver.current_url:
                return True
            try:
                element = driver.find_element(*locator)
                if not element.is_displayed() or not element.is_enabled():
                    return False
                element.click()
                try:
                    WebDriverWait(driver, 1).until(
                        lambda current_driver: url_part in current_driver.current_url
                    )
                    return True
                except TimeoutException:
                    pass
            except (
                ElementClickInterceptedException,
                NoSuchElementException,
                StaleElementReferenceException,
            ):
                pass
            if url_part in driver.current_url:
                return True
            try:
                fallback_element = driver.find_element(*locator)
                # На текущем Chrome native click иногда не dispatch-ит React-событие.
                driver.execute_script("arguments[0].click();", fallback_element)
            except (
                ElementClickInterceptedException,
                NoSuchElementException,
                StaleElementReferenceException,
            ):
                return False
            return url_part in driver.current_url

        self.wait.until(
            click_and_check_url,
            message=f"Переход по {locator} к URL с фрагментом {url_part!r} не выполнен",
        )
