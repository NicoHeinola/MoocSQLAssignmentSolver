import json
import time
from typing import List

from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


class AnswerGet:
    def __init__(self):
        self._driver: webdriver.Firefox = None

    def create_driver(self):
        if self._driver is None:
            self._driver = webdriver.Firefox()

    def close_driver(self):
        self._driver.quit()

    def _wait_until_loaded(self, id_of_element):
        delay = 3  # seconds
        try:
            WebDriverWait(self._driver, delay).until(EC.presence_of_element_located((By.ID, id_of_element)))
            return True
        except TimeoutException:
            return False

    def _wait_until_loaded_xpath(self, xpath_of_element):
        delay = 3  # seconds
        try:
            WebDriverWait(self._driver, delay).until(EC.presence_of_element_located((By.XPATH, xpath_of_element)))
            return True
        except TimeoutException:
            return False

    def _wait_for_element_text(self, element: WebElement, text: str):
        delay = 3  # seconds
        try:
            WebDriverWait(self._driver, delay).until(lambda e: element.text == text)
            return True
        except TimeoutException:
            return False

    def _check_if_alert(self, delay: float = 0.5) -> bool:
        try:
            WebDriverWait(self._driver, delay).until(EC.alert_is_present())

            alert = self._driver.switch_to.alert
            alert.accept()
            return True
        except TimeoutException:
            return False

    def _logout(self) -> bool:
        logout_button: WebElement = self._driver.find_element_by_id("menu").find_element_by_tag_name("button")
        if self._wait_for_element_text(logout_button, "Kirjaudu ulos"):
            logout_button.click()
            return True
        return False

    def _login(self, username: str, password: str) -> bool:
        self._logout()

        self._driver.find_element_by_id("username").send_keys(username)
        self._driver.find_element_by_id("password").send_keys(password)
        self._driver.find_element_by_id("menu").find_element_by_tag_name("button").click()

        return not self._check_if_alert(delay=7)

    def _find_finished_tasks(self):
        task_divs: List[WebElement] = self._driver.find_element_by_id("menu").find_element_by_tag_name("tbody").find_elements_by_tag_name("div")
        done_tasks: List[int] = []
        for div in task_divs:
            bg: str = div.value_of_css_property("background")
            if "rgb(144, 238, 144)" in bg:
                done_tasks.append(int(div.text))
        return done_tasks

    def _get_task_solution(self, task_num: int):
        self._driver.get(f"https://sqltrainer.withmooc.fi/#{task_num}")
        self._wait_until_loaded_xpath("/html/body/table/tbody/tr/td[1]/div/div[2]/span")
        self._driver.find_element_by_xpath("/html/body/table/tbody/tr/td[1]/div/div[2]/span").click()  # clicks the button that shows solution
        self._wait_until_loaded_xpath("/html/body/table/tbody/tr/td[1]/div/div[2]/textarea")
        return self._driver.find_element_by_xpath("/html/body/table/tbody/tr/td[1]/div/div[2]/textarea").get_attribute("value")

    def save_answers(self, username: str, password: str) -> bool:
        url = r"https://sqltrainer.withmooc.fi"
        self._driver.get(url)
        self._wait_until_loaded("username")
        login_check1: bool = self._login(username, password)
        # login_check2: bool = self._wait_for_element_text(self._driver.find_element_by_id("menu").find_element_by_tag_name("button"), "Kirjaudu ulos")
        if not login_check1:
            print("Could not login!")
            return False
        else:
            print("Logged in successfully")

        done_tasks: List[int] = self._find_finished_tasks()

        solutions: dict = {}
        for i, task in enumerate(done_tasks):
            solution: str = self._get_task_solution(task)
            solutions[task] = solution

        # Saves the data
        with open('answers.json', 'w', encoding='utf-8') as f:
            json.dump({"answers": solutions}, f, ensure_ascii=False, indent=4)

        return True
