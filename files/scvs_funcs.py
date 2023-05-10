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

class NoAuditedException(Exception):
    "Exception for when no audited financials are available"
    pass

def update():
    content = list(pd.read_csv(r"..\exps.txt",sep = "\t",encoding = "latin-1")["EXPEDIENTE"])
    a = os.listdir("Financials")
    for i in a:
        content.remove(int(i))
    return content

def solve(src):
    #Save and Read the captcha image
    ur.urlretrieve(src,"captcha.png")
    #Gaming PC
    # pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    #DHUB PC
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
                By.ID,"frmMenu:menuDocumentacion")))
        btn.click()

        #In case captcha comes up, solve it:
        time.sleep(0.25)
        solve_other(driver)
        time.sleep(0.25)

        #Open the Economic Documents tab
        driver.find_elements(By.CLASS_NAME,"ui-tabs-header.ui-state-default.ui-corner-top")[2].click()
  
  #In case captcha comes up, solve it:
        time.sleep(0.25)
        solve_other(driver)
        time.sleep(0.25)

        print("Financial Info Opened Successfully")
        fails = 0
    except (TimeoutException,ElementNotInteractableException,ElementClickInterceptedException,HTTPError,NoSuchElementException):
        print("Nav. to financial failed")
        fails += 1
        driver.refresh()
        if fails < 10:
            print(f"Fail number {fails}")
            navFin(driver,fails)
        else:
            print("Too many failures")
            raise PlannedException("Too many failures.")
            
def auditedShow(driver):
    time.sleep(1)
    wait = WebDriverWait(driver,10,0.2)
    wait.until(EC.visibility_of_element_located((By.ID,"frmInformacionCompanias:tabViewDocumentacion:tblDocumentosEconomicos")))
    #Find the adequate information table.
    m_table = driver.find_element(By.ID,"frmInformacionCompanias:tabViewDocumentacion:tblDocumentosEconomicos")
    #Find the pertinent search bar with the proper search criteria.
    s_bar = m_table.find_element(By.CLASS_NAME,"ui-column-filter.ui-inputfield.ui-inputtext.ui-widget.ui-state-default.ui-corner-all")
    s_bar.send_keys("AUD")
    #Display every single document possible
    elements = Select(m_table.find_element(By.CSS_SELECTOR,
                        "select.ui-paginator-rpp-options.ui-widget.ui-state-default.ui-corner-left"))
    elements.select_by_visible_text("*")
    #Audited Financials won't always be available. If it's the case, then extract every statement separately.
    #Wait until the table updates to check if there are any elements to download.
    time.sleep(1)
    wait.until(EC.element_to_be_clickable(m_table))
    # m_table.click()
 
    if len(m_table.find_elements(By.CLASS_NAME,"ui-widget-content.ui-datatable-even")) == 0:
        print("No audited financial statements found. Resorting to downloading the regular financials")
        s_bar.send_keys(Keys.CONTROL + "a")
        s_bar.send_keys(Keys.DELETE)
        time.sleep(0.5)
        wait.until(EC.element_to_be_clickable(s_bar))
        raise NoAuditedException
    time.sleep(3)
    
def finShow(driver,crit):
    print(crit)
    time.sleep(5)
    wait = WebDriverWait(driver,10,0.2)
    wait.until(EC.element_to_be_clickable((By.ID,"frmInformacionCompanias:tabViewDocumentacion:tblDocumentosEconomicos")))
    #Find the adequate information table.
    m_table = driver.find_element(By.ID,"frmInformacionCompanias:tabViewDocumentacion:tblDocumentosEconomicos")
    #Find the pertinent search bar with the proper search criteria.
    s_bar = m_table.find_element(By.CLASS_NAME,"ui-column-filter.ui-inputfield.ui-inputtext.ui-widget.ui-state-default.ui-corner-all")
    s_bar.send_keys(Keys.CONTROL + "a")
    s_bar.send_keys(Keys.DELETE)
    time.sleep(5)
    s_bar.send_keys(crit)
    
    #Solve Captcha if it pops up
    time.sleep(0.5)
    solve_other(driver)
    time.sleep(0.5)

    #Display every single document possible
    elements = Select(m_table.find_element(By.CSS_SELECTOR,
                        "select.ui-paginator-rpp-options.ui-widget.ui-state-default.ui-corner-left"))
    elements.select_by_visible_text("*")

    #Solve Captcha if it pops up
    time.sleep(0.5)
    solve_other(driver)
    time.sleep(0.5)
 
def join(rows_u):
    d = []
    for i in rows_u:
        d.extend(i)
    return d

def separator(crit,p):
    print(f"Path for separator: {p}")
    if not os.path.isdir(f"{p}\\{crit}"):
        with open(f"{p}\\{crit}","w") as f:
            f.write(" ")

def download(driver,p,count = 0,fails = 0,audit = True, crit = "AUD"):
    a = audit
    print(p)
    print(f"Audit = {a}")
    wait = WebDriverWait(driver,10)
    try:
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
            wait.until(EC.element_to_be_clickable((By.ID,"frmInformacionCompanias:tabViewDocumentacion:tblDocumentosEconomicos")))
            m_table = driver.find_element(By.ID,"frmInformacionCompanias:tabViewDocumentacion:tblDocumentosEconomicos")
            rows_p = m_table.find_elements(By.CLASS_NAME,"ui-widget-content.ui-datatable-even")
            rows_i = m_table.find_elements(By.CLASS_NAME,"ui-widget-content.ui-datatable-odd")
            rows_u = zip(rows_p,rows_i)
            rows = join(rows_u)

            #Are there any documents?
            if len(m_table.find_elements(By.CLASS_NAME,"ui-widget-content.ui-datatable-even")) == 0 and audit == True:
                print("No audited financials")
                raise NoAuditedException
            separator(crit,p)
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
                action.move_to_element_with_offset(x,360,-225)
                action.click()
                action.perform()
                time.sleep(3)
            else:
                #Download Button (After first download)
                action.move_to_element_with_offset(x,365,-210)
                action.click()
                action.perform()
           #X Button (After first download)
            action.move_to_element_with_offset(x,450,-240)
            action.click()
            action.perform()
            #Check if file was actually downloaded
            print(f"New amount of files in dir: {len(os.listdir(p))}")
            if file_num == len(os.listdir(p)):
                if fails > 10:
                    print("Documents consistently not downloading. Starting again.")
                    raise PlannedException("Documents consistently not downloading. Starting again.")
                driver.refresh()
                fails += 1
                
                print("No file was downloaded. Repeating iteration...")
                navFin(driver)
                time.sleep(1)
                #Download the right kind of documents.
                if audit == True:
                    auditedShow(driver)
                else:
                    finShow(driver,crit)
                download(driver = driver,p = p,
                        count = count,fails = fails,audit = a,crit = crit)
            count += 1      
    except (TimeoutException,ElementNotInteractableException,ElementClickInterceptedException,HTTPError) as e:
        print("Load Failed...")
        driver.refresh()
        navFin(driver)
        time.sleep(3)
        #Download the right kind of documents.
        if audit == True:
            auditedShow(driver)
        else:
            finShow(driver,crit)
        download(driver = driver,p = p,
                 count = count,fails = fails,audit = a,crit = crit)
    except NoSuchElementException:
        print("No PDF available for this year")
        count += 1
        print("Load Failed...")
        driver.refresh()
        navFin(driver)
        time.sleep(3)
        if audit == True:
            print("Audit is equal to true")
            auditedShow(driver)
        else:
            print(f"Here, Audit is equal to:{audit}")
            finShow(driver,crit)
            download(driver = driver,
                     p = p,count = count,fails = fails,audit = a,crit = crit)

    except IndexError:
        print("No more PDFs")