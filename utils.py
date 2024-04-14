from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement


def create_driver():
    options = ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options)

    return driver


def remove_elements(driver: WebDriver, *elements: WebElement):
    with open("./js/remove_elems.js", mode='r') as f:
        script = f.read()

    driver.execute_script(script, *elements)
