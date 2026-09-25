"""Домашнее задание 4: ожидания Selenium.

Условие 1:
Открыть http://uitestingplayground.com/textinput, ввести «ITCH» в поле,
нажать синюю кнопку и проверить, что текст кнопки стал «ITCH».

Условие 2:
Открыть https://bonigarcia.dev/selenium-webdriver-java/loading-images.html,
дождаться загрузки всех изображений, получить атрибут alt третьего изображения
и проверить, что он равен «award».

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


@pytest.fixture()
def driver():
    browser = webdriver.Chrome()
    yield browser
    browser.quit()


def test_text_input_changes_button_name(driver):
    driver.get("http://uitestingplayground.com/textinput")
    wait = WebDriverWait(driver, 10)

    input_field = wait.until(
        EC.visibility_of_element_located((By.ID, "newButtonName"))
    )
    input_field.clear()
    input_field.send_keys("ITCH")

    button = wait.until(
        EC.element_to_be_clickable((By.ID, "updatingButton"))
    )
    button.click()

    wait.until(
        EC.text_to_be_present_in_element((By.ID, "updatingButton"), "ITCH")
    )
    assert button.text == "ITCH"


def test_third_loaded_image_has_award_alt(driver):
    driver.get(
        "https://bonigarcia.dev/selenium-webdriver-java/loading-images.html"
    )
    wait = WebDriverWait(driver, 15)

    def images_loaded(browser):
        images = browser.find_elements(By.CSS_SELECTOR, "#image-container img")
        if len(images) != 4:
            return False

        all_images_loaded = all(
            browser.execute_script(
                "return arguments[0].complete && arguments[0].naturalWidth > 0;",
                image,
            )
            for image in images
        )
        return images if all_images_loaded else False

    images = wait.until(images_loaded)

    assert images[2].get_attribute("alt") == "award"
