"""Page Object корзины SauceDemo."""

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


class CartPage:
    """Операции с корзиной."""

    CHECKOUT_BUTTON = (By.ID, "checkout")

    def __init__(self, driver: WebDriver, timeout: int = 15) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def checkout(self) -> None:
        """Переходит к оформлению заказа."""
        self.wait.until(EC.presence_of_element_located(self.CHECKOUT_BUTTON))
        self._click_and_wait_for_url(
            self.CHECKOUT_BUTTON,
            "/checkout-step-one.html",
        )

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
