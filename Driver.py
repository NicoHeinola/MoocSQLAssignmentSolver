import os
import requests
import zipfile

class Driver:
    @staticmethod
    def geckodriver_exists() -> bool:
        return os.path.exists("./geckodriver.exe")

    @staticmethod
    def download_driver():
        url = r"https://github.com/mozilla/geckodriver/releases/download/v0.31.0/geckodriver-v0.31.0-win64.zip"
        r = requests.get(url)
        with open('geckodriver.zip', 'wb') as file:
            file.write(r.content)

        with zipfile.ZipFile("./geckodriver.zip","r") as file:
            file.extractall()

        os.remove("geckodriver.zip")