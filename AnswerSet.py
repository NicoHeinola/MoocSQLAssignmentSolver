import json
import time
from typing import List
import os

from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


class AnswerSet:
    def __init__(self):
        self._driver: webdriver.Firefox = None

    def close_driver(self):
        self._driver.quit()

    def create_driver(self):
        if self._driver is None:
            self._driver = webdriver.Firefox()

    def _wait_until_loaded(self, id_of_element):
        delay = 3  # seconds
        try:
            WebDriverWait(self._driver, delay).until(EC.presence_of_element_located((By.ID, id_of_element)))
            return True
        except TimeoutException:
            return False

    def _wait_until_loaded_xpath(self, xpath_of_element):
        delay = 10  # seconds
        try:
            WebDriverWait(self._driver, delay).until(EC.presence_of_element_located((By.XPATH, xpath_of_element)))
            return True
        except TimeoutException:
            return False

    def _wait_for_element_text(self, element: WebElement, text: str):
        delay = 10  # seconds
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

    def _solve_sql(self, task_num: int, solution: str):
        self._driver.get(fr"https://sqltrainer.withmooc.fi/#{task_num}")
        time.sleep(0.2)
        self._wait_until_loaded("query")
        self._wait_until_loaded("submit")

        query = self._driver.find_element_by_xpath('//*[@id="query"]')
        query.clear()
        query.send_keys(solution)
        submit = self._driver.find_element_by_xpath(r'//*[@id="submit"]')
        submit.click()

        w = self._wait_until_loaded_xpath("/html/body/table/tbody/tr/td[1]/div/span/font")
        if w:
            print(f"{task_num}: Solved")
        else:
            print(f"{task_num}: Was unable to solve")

    def insert_answers(self, username: str, password: str) -> bool:
        url = r"https://sqltrainer.withmooc.fi"
        self._driver.get(url)
        self._wait_until_loaded("username")
        login_check1: bool = self._login(username, password)
        if not login_check1:
            print("Could not login!")
            return False
        else:
            print("Logged in successfully")

        # Loads correct answers
        if os.path.exists("./answers.json"):
            with open('answers.json', 'r', encoding='utf-8') as f:
                data = json.load(f)["answers"]
        else:
            print("Could not find answers.json")
            print("Using hard-coded answers...")
            data = {
                "1": "SELECT nimi FROM Elokuvat;",
                "2": "SELECT nimi, vuosi FROM Elokuvat;",
                "3": "SELECT nimi FROM Elokuvat WHERE vuosi=1940;",
                "4": "SELECT nimi FROM Elokuvat WHERE vuosi<1950;",
                "5": "SELECT nimi FROM Elokuvat WHERE vuosi BETWEEN 1940 AND 1950;",
                "6": "SELECT nimi FROM Elokuvat WHERE vuosi<1950 OR vuosi>1980;",
                "7": "SELECT nimi FROM Elokuvat WHERE vuosi<>1940;",
                "8": "SELECT nimi FROM Elokuvat ORDER BY nimi;",
                "9": "SELECT nimi FROM Elokuvat ORDER BY nimi DESC;",
                "10": "SELECT nimi, vuosi FROM Elokuvat ORDER BY vuosi DESC, nimi;",
                "11": "SELECT DISTINCT etunimi FROM Nimet;",
                "12": "SELECT DISTINCT etunimi, sukunimi FROM Nimet;",
                "13": "SELECT COUNT(*) FROM Tyontekijat;",
                "14": "SELECT COUNT(*) FROM Tyontekijat WHERE palkka>2000;",
                "15": "SELECT SUM(palkka) FROM Tyontekijat;",
                "16": "SELECT MAX(palkka) FROM Tyontekijat;",
                "17": "SELECT COUNT(DISTINCT yritys) FROM Tyontekijat;",
                "18": "SELECT yritys, COUNT(*) FROM Tyontekijat GROUP BY yritys;",
                "19": "SELECT yritys, MAX(palkka) FROM Tyontekijat GROUP BY yritys;",
                "20": "SELECT yritys, MAX(palkka) FROM Tyontekijat GROUP BY yritys HAVING MAX(palkka)>=5000;",
                "21": "SELECT P.nimi, T.tulos FROM Pelaajat P, Tulokset T WHERE P.id=T.pelaaja_id;",
                "22": "SELECT P.nimi, T.tulos FROM Pelaajat P, Tulokset T WHERE P.id=T.pelaaja_id AND P.nimi='Uolevi';",
                "23": "SELECT P.nimi, T.tulos FROM Pelaajat P, Tulokset T WHERE P.id=T.pelaaja_id AND T.tulos>250;",
                "24": "SELECT P.nimi, T.tulos FROM Pelaajat P, Tulokset T WHERE P.id=T.pelaaja_id ORDER BY T.tulos DESC, P.nimi;",
                "25": "SELECT P.nimi, MAX(T.tulos) FROM Pelaajat P, Tulokset T WHERE P.id=T.pelaaja_id GROUP BY P.id;",
                "26": "SELECT P.nimi, COUNT(T.tulos) FROM Pelaajat P, Tulokset T WHERE P.id=T.pelaaja_id GROUP BY P.id;",
                "27": "SELECT O.nimi, K.nimi, S.arvosana FROM Opiskelijat O, Kurssit K, Suoritukset S WHERE O.id=S.opiskelija_id AND K.id=S.kurssi_id;",
                "28": "SELECT K.nimi, S.arvosana FROM Opiskelijat O, Kurssit K, Suoritukset S WHERE O.id=S.opiskelija_id AND K.id=S.kurssi_id AND O.nimi='Uolevi';",
                "29": "SELECT O.nimi, S.arvosana FROM Opiskelijat O, Kurssit K, Suoritukset S WHERE O.id=S.opiskelija_id AND K.id=S.kurssi_id AND K.nimi='Ohpe';",
                "30": "SELECT O.nimi, K.nimi, S.arvosana FROM Opiskelijat O, Kurssit K, Suoritukset S WHERE O.id=S.opiskelija_id AND K.id=S.kurssi_id AND S.arvosana BETWEEN 4 AND 5;",
                "31": "SELECT O.nimi, COUNT(*) FROM Opiskelijat O, Suoritukset S WHERE O.id=S.opiskelija_id GROUP BY O.id;",
                "32": "SELECT O.nimi, MAX(S.arvosana) FROM Opiskelijat O, Suoritukset S WHERE O.id=S.opiskelija_id GROUP BY O.id;",
                "33": "SELECT A.nimi, B.nimi FROM Kaupungit A, Kaupungit B, Lennot L WHERE L.mista_id=A.id AND L.minne_id=B.id;",
                "34": "SELECT B.nimi FROM Kaupungit A, Kaupungit B, Lennot L WHERE L.mista_id=A.id AND L.minne_id=B.id AND A.nimi='Helsinki';",
                "35": "SELECT P.nimi, COUNT(T.tulos) FROM Pelaajat P LEFT JOIN Tulokset T ON P.id=T.pelaaja_id GROUP BY P.id;",
                "36": "SELECT O.nimi, COUNT(S.arvosana) FROM Opiskelijat O LEFT JOIN Suoritukset S ON O.id=S.opiskelija_id GROUP BY O.id;",
                "37": "SELECT K.nimi, COUNT(S.arvosana) FROM Kurssit K LEFT JOIN Suoritukset S ON K.id=S.kurssi_id GROUP BY K.id;",
                "38": "SELECT DISTINCT K.nimi FROM Kurssit K, Suoritukset S WHERE K.id=S.kurssi_id;",
                "39": "SELECT K.nimi FROM Kurssit K LEFT JOIN Suoritukset S ON K.id=S.kurssi_id GROUP BY K.id HAVING COUNT(S.arvosana)=0;",
                "40": "SELECT K.nimi, COUNT(L.minne_id) FROM Kaupungit K LEFT JOIN Lennot L ON K.id=L.mista_id GROUP BY K.id;",
                "41": "SELECT nimi, hinta*2 FROM Tuotteet;",
                "42": "SELECT nimi, hinta FROM Tuotteet WHERE hinta%2=0;",
                "43": "SELECT sana, LENGTH(sana) FROM Sanat;",
                "44": "SELECT sana FROM Sanat WHERE LENGTH(sana)<6;",
                "45": "SELECT sana FROM Sanat ORDER BY LENGTH(sana), sana;",
                "46": "SELECT etunimi || ' ' || sukunimi FROM Kayttajat;",
                "47": "SELECT SUM(LENGTH(sana)) FROM Sanat;",
                "48": "SELECT tuote, hinta*maara FROM Tilaukset;",
                "49": "SELECT SUM(hinta*maara) FROM Tilaukset;",
                "50": "SELECT nimi FROM Elokuvat WHERE vuosi%4=0 AND (vuosi%100<>0 OR vuosi%400=0);",
                "51": "SELECT nimi FROM Tuotteet WHERE hinta=(SELECT MIN(hinta) FROM Tuotteet);",
                "52": "SELECT nimi FROM Tuotteet WHERE hinta <= 2*(SELECT MIN(hinta) FROM Tuotteet);",
                "53": "SELECT nimi FROM Tuotteet WHERE hinta IN (SELECT hinta FROM Tuotteet GROUP BY hinta HAVING COUNT(*)=1);",
                "54": "SELECT MIN(sana) FROM Sanat;",
                "55": "SELECT sana FROM Sanat ORDER BY sana LIMIT 1 OFFSET 1;",
                "56": "SELECT sana FROM Sanat ORDER BY sana LIMIT (SELECT COUNT(*)-1 FROM Sanat) OFFSET 1;",
                "57": "SELECT sana FROM Sanat WHERE sana LIKE '%i%';",
                "58": "SELECT sana FROM Sanat WHERE sana LIKE 'a%';",
                "59": "SELECT sana FROM Sanat WHERE sana LIKE '_p___';",
                "60": "SELECT sana FROM Sanat WHERE sana LIKE '%a%a%' AND sana NOT LIKE '%a%a%a%';",
                "61": "SELECT K.tunnus, COUNT(O.ryhma_id) FROM Kayttajat K LEFT JOIN Oikeudet O ON K.id=O.kayttaja_id GROUP BY K.id;",
                "62": "SELECT R.nimi, COUNT(O.kayttaja_id) FROM Ryhmat R LEFT JOIN Oikeudet O ON R.id=O.ryhma_id GROUP BY R.id;",
                "63": "SELECT K.tunnus FROM Kayttajat K LEFT JOIN Oikeudet O ON K.id=O.kayttaja_id GROUP BY K.id HAVING COUNT(O.ryhma_id) > 1;",
                "64": "SELECT DISTINCT A.tunnus FROM Kayttajat A, Kayttajat B, Oikeudet X, Oikeudet Y WHERE A.id=X.kayttaja_id AND B.id=Y.kayttaja_id AND X.ryhma_id=Y.ryhma_id AND B.tunnus='uolevi';",
                "65": "SELECT tunnus FROM Kayttajat WHERE tunnus NOT IN (SELECT A.tunnus FROM Kayttajat A, Kayttajat B, Oikeudet X, Oikeudet Y WHERE A.id=X.kayttaja_id AND B.id=Y.kayttaja_id AND X.ryhma_id=Y.ryhma_id AND B.tunnus='uolevi');",
                "66": "SELECT sana FROM Sanat ORDER BY LOWER(sana);",
                "67": "SELECT nimi, hinta FROM Tuotteet ORDER BY hinta, nimi LIMIT 1;",
                "68": "SELECT A.nimi, COUNT(*) FROM Tuotteet A, Tuotteet B WHERE ABS(A.hinta-B.hinta) <= 1 GROUP BY A.id;",
                "69": "SELECT COUNT(*) FROM Tuotteet A, Tuotteet B WHERE A.hinta+B.hinta=10 AND A.id <= B.id;",
                "70": "SELECT MIN(ABS(A.hinta-B.hinta)) FROM Tuotteet A, Tuotteet B WHERE A.id<>B.id;",
                "71": "SELECT A.haltija, IFNULL(SUM(B.muutos),0) FROM Tilit A LEFT JOIN Tapahtumat B ON A.id=B.tili_id GROUP BY A.id;",
                "72": "SELECT SUM(B.muutos) FROM Tilit T, Tapahtumat A, Tapahtumat B WHERE A.tili_id=T.id AND B.tili_id=T.id AND T.haltija=\"Uolevi\" AND B.id<=A.id GROUP BY A.id;",
                "73": "SELECT haltija, IFNULL((SELECT MAX((SELECT SUM(muutos) FROM Tapahtumat WHERE tili_id=B.id AND id <= A.id)) FROM Tapahtumat A),0) FROM Tilit B;",
                "74": "SELECT O.nimi, COUNT(DISTINCT L.tehtava_id) FROM Opiskelijat O LEFT JOIN Lahetykset L ON O.id=L.opiskelija_id AND L.tila=1 GROUP BY O.id;",
                "75": "SELECT nimi, IFNULL((SELECT MAX(maara) FROM (SELECT COUNT(*) maara FROM Lahetykset WHERE opiskelija_id=O.id GROUP BY tehtava_id)),0) FROM Opiskelijat O;",
                "76": "SELECT tulos FROM Tulokset GROUP BY tulos ORDER BY COUNT(*) DESC, tulos LIMIT 1;",
                "77": "SELECT tulos FROM Tulokset ORDER BY tulos LIMIT 1 OFFSET (SELECT COUNT(*)/2 FROM Tulokset);",
                "78": "SELECT tulos FROM Tulokset ORDER BY tulos LIMIT 1 OFFSET (SELECT (COUNT(*)-1)/2 FROM Tulokset);",
                "79": "SELECT V.nimi, COUNT(M.id) FROM Vaunut V LEFT JOIN Matkustajat M ON V.id=M.vaunu_id GROUP BY V.id;",
                "80": "SELECT V.nimi, V.paikat-COUNT(M.id) FROM Vaunut V LEFT JOIN Matkustajat M ON V.id=M.vaunu_id GROUP BY V.id;",
                "81": "SELECT (SELECT SUM(paikat) FROM vaunut)-(SELECT COUNT(*) FROM Matkustajat);"
            }

        for key in data:
            self._solve_sql(int(key), data[key])

        return True
