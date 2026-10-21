"""Page Object страницы оформления заказа SauceDemo."""

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


class CheckoutPage:
    """Операции с формой заказа и итоговой стоимостью."""

    FIRST_NAME_INPUT = (By.ID, "first-name")
    LAST_NAME_INPUT = (By.ID, "last-name")
    POSTAL_CODE_INPUT = (By.ID, "postal-code")
    CONTINUE_BUTTON = (By.ID, "continue")
    TOTAL_LABEL = (By.CSS_SELECTOR, "[data-test='total-label']")

    def __init__(self, driver: WebDriver, timeout: int = 15) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def fill_customer_data(
        self,
        first_name: str,
        last_name: str,
        postal_code: str,
    ) -> None:
        """Заполняет данные покупателя и переходит к итогам заказа."""
        fields = (
            ("имя", self.FIRST_NAME_INPUT, first_name),
            ("фамилия", self.LAST_NAME_INPUT, last_name),
            ("почтовый индекс", self.POSTAL_CODE_INPUT, postal_code),
        )
        for field_name, locator, value in fields:
            field = self.wait.until(
                EC.visibility_of_element_located(locator),
                message=f"Поле checkout ({field_name}) не появилось",
            )
            field.send_keys(value)
            self._ensure_field_value(locator, value, field_name)

        self._click_and_wait_for_url(
            self.CONTINUE_BUTTON,
            "/checkout-step-two.html",
        )

    def get_total(self) -> str:
        """Возвращает итоговую стоимость без префикса ``Total:``."""
        total_text = self.wait.until(
            EC.visibility_of_element_located(self.TOTAL_LABEL)
        ).text
        return total_text.removeprefix("Total: ").strip()

    def _ensure_field_value(
        self,
        locator: tuple[str, str],
        value: str,
        field_name: str,
    ) -> None:
        """Проверяет значение React-input и при необходимости устанавливает его."""

        def value_is_expected(driver: WebDriver) -> bool:
            return driver.find_element(*locator).get_attribute("value") == value

        try:
            WebDriverWait(self.driver, 1).until(value_is_expected)
            return
        except TimeoutException:
            field = self.wait.until(
                EC.visibility_of_element_located(locator),
                message=f"Поле checkout ({field_name}) не сохранило значение",
            )
            self.driver.execute_script(
                "const input = arguments[0];"
                "const value = arguments[1];"
                "const setter = Object.getOwnPropertyDescriptor("
                "HTMLInputElement.prototype, 'value').set;"
                "setter.call(input, value);"
                "input.dispatchEvent(new Event('input', {bubbles: true}));"
                "input.dispatchEvent(new Event('change', {bubbles: true}));",
                field,
                value,
            )
            self.wait.until(
                value_is_expected,
                message=f"Поле checkout ({field_name}) не сохранило значение",
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
