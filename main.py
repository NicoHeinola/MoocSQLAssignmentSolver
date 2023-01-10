import os
import sys
import threading
import time

from AnswerGet import AnswerGet
from AnswerSet import AnswerSet
from Driver import Driver

from threading import Thread

if __name__ == '__main__':

    print("Load: Loads all correct answers from your SQL assignments into a json-file")
    print("Solve: Automatically solves most of your SQL assignments")
    mode: str = input("Do you want to load or solve answers? (L/S): ")

    if not Driver.geckodriver_exists():
        do_download = input("geckodriver.exe is missing...\nDo you want to download geckodriver? (Y/N): ")
        if do_download.lower() == "y":
            print("Downloading...")
            Driver.download_driver()
        else:
            print("Stopping program...")
            sys.exit()

    if mode.lower() == "l":
        answer_get: AnswerGet = AnswerGet()
        start_driver_thread: Thread = Thread(target=lambda: answer_get.create_driver())
        start_driver_thread.start()
    else:
        answer_set: AnswerSet = AnswerSet()
        start_driver_thread: Thread = Thread(target=lambda: answer_set.create_driver())
        start_driver_thread.start()

    if Driver.geckodriver_exists():
        while True:
            username: str = input("Please type your username: ")
            password: str = input('Please type your password: ')
            os.system("cls")

            if start_driver_thread.is_alive():
                print("Waiting for browser to start...")
                while start_driver_thread.is_alive():
                    time.sleep(0.1)

            if mode.lower() == "l":
                success: bool = answer_get.save_answers(username, password)
                if success:
                    answer_get.close_driver()
            else:
                success: bool = answer_set.insert_answers(username, password)
                if success:
                    answer_set.close_driver()

            if not success:
                restart = input("Do you want to restart the program? (Y/N): ")
                if restart.lower() != "y":
                    break
            else:
                print("Program has finished...")
                sys.exit()
