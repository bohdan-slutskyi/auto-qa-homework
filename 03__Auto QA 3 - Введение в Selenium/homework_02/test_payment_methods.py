from pathlib import Path
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By


BASE_URL = "https://itcareerhub.de/ru/"
SCREENSHOT_PATH = Path(__file__).parent / "artifacts" / "payment_methods_section.png"


def main() -> None:
    SCREENSHOT_PATH.parent.mkdir(exist_ok=True)
    driver = webdriver.Chrome()
    driver.fullscreen_window()

    try:
        driver.get(BASE_URL)
        sleep(3)

        cookie_buttons = driver.find_elements(
            By.XPATH,
            "//button[.//span[normalize-space()='Accept essential only']]",
        )
        if cookie_buttons:
            cookie_buttons[0].click()
            sleep(1)

        menu_buttons = driver.find_elements(By.CSS_SELECTOR, 'a[href="#menuopen"]')
        if menu_buttons and menu_buttons[0].is_displayed():
            driver.execute_script("arguments[0].click();", menu_buttons[0])
            sleep(1)

        payment_methods_links = driver.find_elements(By.LINK_TEXT, "Способы оплаты")
        for payment_methods_link in payment_methods_links:
            if payment_methods_link.is_displayed():
                driver.execute_script("arguments[0].click();", payment_methods_link)
                break
        sleep(2)

        if not driver.save_screenshot(str(SCREENSHOT_PATH)):
            raise RuntimeError("Не удалось сохранить скриншот страницы.")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
