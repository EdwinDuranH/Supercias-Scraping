from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException,TimeoutException,ElementNotInteractableException,ElementClickInterceptedException,NoSuchElementException,UnexpectedAlertPresentException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.select import Select
import pandas as pd
import cv2
import pytesseract
import os
import urllib.request as ur
import html5lib
from bs4 import BeautifulSoup
import os
from urllib.error import HTTPError

#Create a custom error so I can use it whenever I want the program to fail
class PlannedException(Exception):
    "Exception for whenever I need a part of the program to fail"
    pass

def update():
    with open("allexps.csv") as f:
        content = f.readlines()
    a = os.listdir("Financials")
    content.remove("expediente\n")
    for i in a:
        content.remove(f"{i}\n")
    for i in range(len(content)):
        content[i] = content[i].replace("\n","")
    return content

def solve(src):
    #Save and Read the captcha image
    ur.urlretrieve(src,"captcha.png")
    #Gaming PC
    pytesseract.pytesseract.tesseract_cmd = r"C:\Users\eduranh\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
    #Other PC
#     pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Py Tesseract\tesseract.exe"
    img = cv2.imread("captcha.png")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    answer = pytesseract.image_to_string(img)
#     print(answer)
    #Remove image after reading it so the next iteration can save a new captcha.
    os.remove("captcha.png")
    return answer

def solve_other(driver):
    answer = 0
    time.sleep(3)
    try:
        captcha = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.ID,"frmCaptcha:captchaImage")))
        src = captcha.get_attribute("src")
        answer = solve(src)
        bar = driver.find_element(By.ID,"frmCaptcha:captcha")
        time.sleep(1)
        bar.send_keys(answer)
        bar.send_keys(Keys.ENTER)
        print("Captcha Solved")
        return answer
    except:
#         print("No Captcha")
        pass
    return answer

def navFin(driver,fails = 0):
    try:
        #Click Yearly Information Tab:
        btn = WebDriverWait(driver,10).until(
            EC.presence_of_element_located((
                By.ID,"frmMenu:menuInformacionAnualPresentada")))
        btn.click()
        time.sleep(2)
        #In case captcha comes up, solve it:
        solve_other(driver)
        print("Financial Info Opened Successfully")
        fails = 0
    except (TimeoutException,ElementNotInteractableException,ElementClickInterceptedException,HTTPError,NoSuchElementException):
        print("Nav. to financial failed")
        fails += 1
        driver.refresh()
        if fails > 10:
            navFin(driver)


def pdfShow(driver):
    time.sleep(5)
#     try:
        #Find the Historical Balance sheets submitted by the company
#     box = WebDriverWait(driver,10).until(EC.element_to_be_clickable((
#         By.CLASS_NAME,"fui-column-filter.ui-inputfield.ui-inputtext.ui-widget.ui-state-default.ui-corner-all")))
    #Seach for Balance Sheets (Only identifiable by class name. Second object with that name)
    wait = WebDriverWait(driver,10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME,"ui-column-filter.ui-inputfield.ui-inputtext.ui-widget.ui-state-default.ui-corner-all")))
    driver.find_elements(
        By.CLASS_NAME,
        "ui-column-filter.ui-inputfield.ui-inputtext.ui-widget.ui-state-default.ui-corner-all")[1].send_keys("3.1.1")
    print("Keys Sent")
    #Solve Captcha if it pops up
    time.sleep(0.5)
    solve_other(driver)
    time.sleep(0.5)
    #Show every document ever uploaded.
    elements = Select(driver.find_element(By.CSS_SELECTOR,
                           "select.ui-paginator-rpp-options.ui-widget.ui-state-default.ui-corner-left"))
    elements.select_by_visible_text("*")
    time.sleep(2)
#     except (TimeoutException,ElementNotInteractableException,ElementClickInterceptedException,HTTPError,NoSuchElementException) as e:
#         print("PDF Showing Failed")
#         print(e)
#         driver.refresh()
#         navFin(driver)
#         time.sleep(5)
#         pdfShow(driver)
def join(rows_u):
    d = []
    for i in rows_u:
        d.extend(i)
    return d

def download(driver,p,count = 0):
    fails = 0
    try:
        wait = WebDriverWait(driver,10)
        print("Beginning Navigation")
        navFin(driver)
        time.sleep(3)
        pdfShow(driver)
        print("Navigation Finished")
        #Fake rows element to start while loop
        rows = range(100)
        #Set an action object to execute clicks on the webpage at will.
        action = ActionChains(driver)
        #Loop until every single file has been downloaded.
        while len(rows[count:]) > 0:
            file_num = len(os.listdir(p))
            print(f"Current amount of files in dir: {file_num}")
            print(f"File number {count}")
            #Rows where the PDFs are:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME,"ui-widget-content.ui-datatable-even")))
            rows_p = driver.find_elements(By.CLASS_NAME,"ui-widget-content.ui-datatable-even")
            rows_i = driver.find_elements(By.CLASS_NAME,"ui-widget-content.ui-datatable-odd")
            rows_u = zip(rows_p,rows_i)
            rows = join(rows_u)

            #Open the desired PDF.
    #         wait.until(EC.element_to_be_clickable((By.CLASS_NAME,"ui-widget-content.ui-datatable-even")))
            pdf = rows[count].find_element(By.CLASS_NAME,"ui-commandlink.ui-widget")
            driver.execute_script("arguments[0].click();",pdf)
            #Solve Captha if it pops up
            time.sleep(0.5)
            solve_other(driver)
            time.sleep(2)
            print("Starting Download")
            #Download the files.
            wait.until(EC.element_to_be_clickable((By.ID,"dlgPresentarDocumentoPdf")))
            x = driver.find_element(By.ID,"dlgPresentarDocumentoPdf")
            if count == 0:
                print("First Download")
        #         Download Button (First Download)
                action.move_to_element_with_offset(x,365,-290)
                action.click()
                action.perform()
                time.sleep(3)
            else:
                #Download Button (After first download)
                action.move_to_element_with_offset(x,365,-270)
                action.click()
                action.perform()
           #X Button (After first download)
            action.move_to_element_with_offset(x,470,-320)
            action.click()
            action.perform()
            #Check if file was actually downloaded
            print(f"New amount of files in dir: {len(os.listdir(p))}")
            if file_num == len(os.listdir(p)):
                print("No file was downloaded. Repeating iteration...")
                driver.refresh()
                download(driver,p,count)
                fails += 1
                if fails > 10:
                    raise PlannedException("Documents consistently not downloading. Starting again.")
            count += 1      
    except (TimeoutException,ElementNotInteractableException,ElementClickInterceptedException,HTTPError,PlannedException) as e:
        print("Load Failed...")
        driver.refresh()
        download(driver,p,count)
    except NoSuchElementException:
        print("No PDF available for this year")
        count += 1
        download(driver,p,count)
    except IndexError:
        print("No more PDFs")