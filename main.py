import os
import time
import datetime
import argparse

import schedule
import pandas as pd
import urllib.parse
from loguru import logger

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from attendance import AttendanceRecord
from utils import create_driver, remove_elements


TIMEOUT = 60
NYCU_PORTAL_TITLE = "國立陽明交通大學 校園單一入口 NYCU Portal"
ATTENDANCE_TITLE = "兼任差勤及服務管理系統"
NYCU_PORTAL_HOME = "https://portal.nycu.edu.tw/#"
LOGIN_PAGE_URL = "/login"
LINK_PAGE_URL = "/links/nycu"
ATTENDANCE_PAGE_URL = "/redirect/attendance"


driver = create_driver()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run_schedule", action="store_true")

    return parser.parse_args()


def login(account: str, password: str):
    login_url = f"{NYCU_PORTAL_HOME}{LOGIN_PAGE_URL}?redirect={urllib.parse.quote(LINK_PAGE_URL, safe='')}"
    driver.get(login_url)

    WebDriverWait(driver, TIMEOUT).until(EC.title_is(NYCU_PORTAL_TITLE))

    f_account = driver.find_element(By.ID, "account")
    f_password = driver.find_element(By.ID, "password")
    f_account.send_keys(account)
    f_password.send_keys(password)
    login_button = driver.find_element(By.CLASS_NAME, "login")
    login_button.click()

    WebDriverWait(driver, TIMEOUT).until(EC.url_to_be(f"{NYCU_PORTAL_HOME}{LINK_PAGE_URL}"))

def check_attendance_records(record_trs: list[WebElement]) -> list[AttendanceRecord]:
    checked_recs = []
    for rec in record_trs:
        rec_id = rec.get_dom_attribute("id")
        if rec_id in [f"grid_grid_rec_{postfix}" for postfix in ["top", "bottom", "more"]]:
            continue
        rec_date = rec.find_element(By.XPATH, "./td[@col='1']/div").text
        rec_status = rec.find_element(By.XPATH, "./td[@col='2']/div").text

        signing_cell = rec.find_element(By.XPATH, "./td/div")
        if (not signing_cell.text) or signing_cell.text.endswith("已送審"):
            continue

        checkbox = signing_cell.find_element(By.TAG_NAME, "input")
        checkbox.click()
        checked_recs.append(AttendanceRecord(id=rec_id, date=rec_date, status=rec_status))

    return checked_recs

def sign_attendances(account, password) -> pd.DataFrame:
    login(account, password)

    driver.get(f"{NYCU_PORTAL_HOME}{ATTENDANCE_PAGE_URL}")
    
    WebDriverWait(driver, TIMEOUT).until(EC.title_is(ATTENDANCE_TITLE))

    time.sleep(1)
    popup = driver.find_element(By.ID, "showWorkLists")
    blocker = driver.find_element(By.CSS_SELECTOR, "div.modal-backdrop.fade.show")
    remove_elements(driver, popup, blocker)

    sign_page_div = driver.find_element(By.ID, "node_level-2-1")
    sign_page_div.click()

    WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.ID, "bugetno")))

    selector = Select(driver.find_element(By.ID, "bugetno"))
    signed_recs = []
    for option in selector.options:
        plan_code = option.get_dom_attribute("value")
        if not plan_code:
            continue

        selector.select_by_value(plan_code)
        WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, "//div[@id='ShowWorkDetail']/div[@id='grid']")))
        rec_table = driver.find_element(By.XPATH, "//div[@id='grid_grid_records']/table/tbody")
        recs = rec_table.find_elements(By.XPATH, "./tr[starts-with(@id, 'grid_grid_rec_')]")
        checked_recs = check_attendance_records(recs)

        submit_button = driver.find_element(By.XPATH, "//input[@value='送審']")
        submit_button.click()

        signed_recs += [(plan_code, rec.id, rec.date, rec.status) for rec in checked_recs]

    return pd.DataFrame(signed_recs, columns=["Plan Code", "Record ID", "Date", "Status"])


if __name__ == "__main__":
    args = parse_args()

    last_signed_date = datetime.date.today()
    account = os.getenv("NYCU_ACCOUNT")
    password = os.getenv("NYCU_PASSWORD")

    def sign_task(month_check=True):
        global last_signed_date

        today = datetime.date.today()
        logger.debug("🔍 Daily check month")
        if (not month_check) or (today.month - last_signed_date.month >= 1):
            logger.info(f"📝 Start signing attendances for {account} ...")
            signed_df = sign_attendances(account, password)

            if signed_df.empty:
                logger.info("👻 No attendances to sign.")
            else:
                logger.info(f"\n✅ Successfully signed records:\n{signed_df.to_string()}")

            last_signed_date = today

    sign_task(month_check=False)  # sign the attendances at the beginning.

    if args.run_schedule:
        schedule.every().day.do(sign_task)
        while True:
            schedule.run_pending()
            time.sleep(1)
