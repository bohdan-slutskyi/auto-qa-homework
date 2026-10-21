"""Page Object каталога SauceDemo."""

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


class InventoryPage:
    """Операции с товарами и переходом в корзину."""

    CART_LINK = (By.CSS_SELECTOR, "[data-test='shopping-cart-link']")

    def __init__(self, driver: WebDriver, timeout: int = 15) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)
        self._added_products_count = 0

    def add_product(self, product_name: str) -> None:
        """Добавляет товар в корзину по его названию."""
        product_slug = product_name.lower().replace(" ", "-")
        product_button = (By.ID, f"add-to-cart-{product_slug}")
        expected_count = self._added_products_count + 1

        def add_and_check_cart_count(driver: WebDriver) -> bool:
            def cart_count_is_expected(current_driver: WebDriver) -> bool:
                try:
                    badge = current_driver.find_element(
                        By.CLASS_NAME,
                        "shopping_cart_badge",
                    )
                except NoSuchElementException:
                    return False
                return badge.text.strip() == str(expected_count)

            if cart_count_is_expected(driver):
                return True
            try:
                button = driver.find_element(*product_button)
                if button.is_displayed() and button.is_enabled():
                    button.click()
                    try:
                        WebDriverWait(driver, 1).until(cart_count_is_expected)
                        return True
                    except TimeoutException:
                        pass
            except (
                ElementClickInterceptedException,
                NoSuchElementException,
                StaleElementReferenceException,
            ):
                pass

            if cart_count_is_expected(driver):
                return True
            try:
                fallback_button = driver.find_element(*product_button)
                # На текущем Chrome native click иногда не dispatch-ит React-событие.
                driver.execute_script("arguments[0].click();", fallback_button)
            except (
                ElementClickInterceptedException,
                NoSuchElementException,
                StaleElementReferenceException,
            ):
                return False
            return cart_count_is_expected(driver)

        self.wait.until(
            add_and_check_cart_count,
            message=(
                f"Товар {product_name!r} не добавился: ожидался badge "
                f"{expected_count}"
            ),
        )
        self._added_products_count = expected_count

    def open_cart(self) -> None:
        """Открывает корзину."""
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.CLASS_NAME, "shopping_cart_badge"),
                str(self._added_products_count),
            )
        )
        self._click_and_wait_for_url(self.CART_LINK, "/cart.html")

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
