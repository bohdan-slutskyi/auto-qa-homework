"""Домашнее задание 6: оформление заказа через Page Object Model.

Условие: открыть SauceDemo, войти как ``standard_user``, добавить в корзину
Sauce Labs Backpack, Sauce Labs Bolt T-Shirt и Sauce Labs Onesie, перейти к
Checkout, заполнить имя, фамилию и почтовый индекс, затем проверить Total
``$58.29``.

Запуск из исходной папки домашнего задания:

    cd "/Users/core/Dev/Auto_QA_Morning_2025_PD/11__Auto QA 11 - Page Object Model/homework"
    "/Users/core/Dev/Auto_QA_Morning_2025_PD/03__Auto QA 3 - Введение в Selenium/practice/selenium_lesson_03/.venv/bin/python" -m pytest -q test_checkout_total.py

Запуск из автономной папки решения:

    uv run --locked pytest -q

Интерпретатор: Python 3.12 в окружении ``.venv``; Selenium Manager сам
подбирает совместимый ChromeDriver.
"""

import pytest
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver

PRODUCTS = (
    "Sauce Labs Backpack",
    "Sauce Labs Bolt T-Shirt",
    "Sauce Labs Onesie",
)


@pytest.fixture()
def driver() -> WebDriver:
    """Создаёт независимый браузер для теста и закрывает его после проверки."""
    browser = webdriver.Chrome()
    browser.set_window_size(1440, 1000)
    try:
        yield browser
    finally:
        browser.quit()


def test_checkout_total_price(driver: WebDriver) -> None:
    """Проверяет итоговую сумму выбранных товаров."""
    login_page = LoginPage(driver)
    inventory_page = InventoryPage(driver)
    cart_page = CartPage(driver)
    checkout_page = CheckoutPage(driver)

    login_page.open()
    login_page.login("standard_user", "secret_sauce")

    for product in PRODUCTS:
        inventory_page.add_product(product)

    inventory_page.open_cart()
    cart_page.checkout()
    checkout_page.fill_customer_data("Test", "User", "12345")

    total = checkout_page.get_total()
    assert total == "$58.29"
