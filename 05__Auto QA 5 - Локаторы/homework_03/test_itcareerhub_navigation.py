"""Домашнее задание 3: локаторы на странице IT Career Hub.

Условие:
Открыть https://itcareerhub.de/ru и проверить наличие логотипа ITCareerHub,
ссылок «Программы», «Способы оплаты», «О нас», «Контакты», «Отзывы» и
«Блог», переключателей языков ru/de. Затем открыть «Контакты», нажать
«Обратный звонок» и проверить текст «Запишитесь на бесплатную карьерную
консультацию» во всплывающем окне.

Запуск из папки этого файла:
    uv run --locked pytest -q

Проверенный интерпретатор на текущем Mac:
    /Users/core/Dev/Auto_QA_Morning_2025_PD/03__Auto QA 3 - Введение в
    Selenium/practice/selenium_lesson_03/.venv/bin/python
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

HOME_PAGE_URL = "https://itcareerhub.de/ru"
CONSULTATION_TEXT = "Запишитесь на бесплатную карьерную консультацию"


@pytest.fixture()
def driver():
    browser = webdriver.Chrome()
    browser.set_window_size(1280, 900)
    yield browser
    browser.quit()


def _visible_element(browser, xpath):
    for element in browser.find_elements(By.XPATH, xpath):
        if element.is_displayed():
            return element
    return False


def test_itcareerhub_navigation_and_callback(driver):
    driver.get(HOME_PAGE_URL)
    wait = WebDriverWait(driver, 15)

    menu_icons = driver.find_elements(
        By.CSS_SELECTOR, 'a[href$="#menuopen"] img'
    )
    for menu_icon in menu_icons:
        if menu_icon.is_displayed():
            menu_icon.click()
            break

    logo = wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, 'img[alt="IT Career Hub"]')
        )
    )
    assert logo.is_displayed()

    for link_text in (
        "Программы",
        "Способы оплаты",
        "О нас",
        "Отзывы",
        "Блог",
    ):
        link = wait.until(
            lambda browser, text=link_text: _visible_element(
                browser, f"//a[normalize-space()='{text}']"
            )
        )
        assert link.is_displayed()

    about_link = wait.until(
        lambda browser: _visible_element(
            browser, "//a[normalize-space()='О нас']"
        )
    )
    about_link.click()

    contacts_link = wait.until(
        lambda browser: _visible_element(
            browser, "//a[normalize-space()='Контакты']"
        )
    )
    assert contacts_link.is_displayed()

    for language in ("ru", "de"):
        language_button = wait.until(
            lambda browser, text=language: _visible_element(
                browser, f"//a[normalize-space()='{text}']"
            )
        )
        assert language_button.is_displayed()

    contacts_link.click()
    wait.until(EC.url_contains("/contact"))

    callback_button = wait.until(
        lambda browser: _visible_element(
            browser,
            "//a[contains(translate(normalize-space(.), "
            "'абвгдеёжзийклмнопрстуфхцчшщъыьэюя', "
            "'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'), "
            "'ОБРАТНЫЙ ЗВОНОК')]",
        )
    )
    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        callback_button,
    )
    driver.execute_script("arguments[0].click();", callback_button)

    popup = wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, ".t-popup.t-popup_show")
        )
    )
    assert CONSULTATION_TEXT in popup.text
