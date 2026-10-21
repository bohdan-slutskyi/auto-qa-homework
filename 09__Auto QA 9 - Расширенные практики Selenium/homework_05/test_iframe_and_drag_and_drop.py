# Auto QA 9: расширенные практики Selenium — домашнее задание 5.
#
# Условие:
# 1. Открыть https://bonigarcia.dev/selenium-webdriver-java/iframes.html,
#    найти iframe с текстом «semper posuere integer et senectus justo curabitur.»
#    и убедиться, что этот текст отображается.
# 2. Открыть https://www.globalsqa.com/demo-site/draganddrop/, перетащить
#    первую фотографию в область Trash и проверить: в корзине 1 фотография,
#    в основной области осталось 3 фотографии.
#
# Запуск из исходной папки проверенным интерпретатором:
#     cd "/Users/core/Dev/Auto_QA_Morning_2025_PD/09__Auto QA 9 - Расширенные практики Selenium/homework"
#     "/Users/core/Dev/Auto_QA_Morning_2025_PD/03__Auto QA 3 - Введение в Selenium/practice/selenium_lesson_03/.venv/bin/python" \
#         -m pytest -q test_iframe_and_drag_and_drop.py
#
# После переноса в автономную папку репозитория:
#     uv run --locked pytest -q

import pytest
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

IFRAMES_URL = "https://bonigarcia.dev/selenium-webdriver-java/iframes.html"
IFRAME_TEXT = "semper posuere integer et senectus justo curabitur."
DRAG_AND_DROP_URL = "https://www.globalsqa.com/demo-site/draganddrop/"


@pytest.fixture()
def driver():
    browser = webdriver.Chrome()
    browser.set_window_size(1440, 1000)
    try:
        yield browser
    finally:
        browser.quit()


def _normalise_text(text: str) -> str:
    """Сворачивает переносы и повторяющиеся пробелы в тексте страницы."""

    return " ".join(text.split())


def test_text_is_present_in_iframe(driver):
    driver.get(IFRAMES_URL)
    wait = WebDriverWait(driver, 15)

    frame = wait.until(
        EC.presence_of_element_located((By.ID, "my-iframe"))
    )
    driver.switch_to.frame(frame)

    try:
        text_is_present = wait.until(
            lambda browser: IFRAME_TEXT
            in _normalise_text(browser.find_element(By.TAG_NAME, "body").text)
        )
        assert text_is_present
    finally:
        driver.switch_to.default_content()


def test_first_photo_is_moved_to_trash(driver):
    driver.get(DRAG_AND_DROP_URL)
    wait = WebDriverWait(driver, 15)

    wait.until(
        EC.frame_to_be_available_and_switch_to_it(
            (By.CSS_SELECTOR, "iframe.demo-frame")
        )
    )

    try:
        gallery_items = wait.until(
            lambda browser: (
                items
                if len(
                    items := browser.find_elements(By.CSS_SELECTOR, "#gallery > li")
                )
                == 4
                else False
            )
        )
        trash = wait.until(
            EC.visibility_of_element_located((By.ID, "trash"))
        )

        ActionChains(driver).drag_and_drop(gallery_items[0], trash).perform()

        wait.until(
            lambda browser: (
                len(browser.find_elements(By.CSS_SELECTOR, "#gallery > li")) == 3
                and len(browser.find_elements(By.CSS_SELECTOR, "#trash ul > li"))
                == 1
            )
        )

        assert len(driver.find_elements(By.CSS_SELECTOR, "#gallery > li")) == 3
        assert len(driver.find_elements(By.CSS_SELECTOR, "#trash ul > li")) == 1
    finally:
        driver.switch_to.default_content()
