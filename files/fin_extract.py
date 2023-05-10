from scvs_funcs import *
#Make master directory to download the files:
if not os.path.isdir("Financials"):
    os.mkdir("Financials")

#Get the absolute path for the master financials directory
path = f"{os.getcwd()}\\Financials"
#Define URL for the info portal
url = "https://appscvsconsultas.supercias.gob.ec/consultaCompanias/societario/busquedaCompanias.jsf"

#Read file with company exps
dframe = list(pd.read_csv(r"..\exps.txt",sep = "\t",encoding = "latin-1")["EXPEDIENTE"])
exps = update()[:1000]
len(exps)

used_rucs = []

while len(exps) != 0:
    used = exps.pop(0)
    #Generate directory for the company's information
    directory = f"Financials\\{used}"
    if not os.path.isdir(directory):
        os.mkdir(directory)       
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs",{"download.default_directory":f"{path}\\{used}",
                                      "download.prompt_for_download":False,
                                      "download.directory_upgrade":True,
                                      "plugins.always_open_pdf_externally":True})
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1004,708)
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 3)
        expedient = wait.until(EC.presence_of_element_located((By.ID,
                                         "frmBusquedaCompanias:parametroBusqueda_input")))
        expedient.send_keys(str(used))
        time.sleep(2)
        expedient.send_keys(Keys.ENTER)
        #Find the Capthca image
        wait = WebDriverWait(driver,3) #Wait element
        captcha = wait.until(EC.presence_of_element_located((By.ID,"frmBusquedaCompanias:captchaImage")))
        src = captcha.get_attribute("src")
        answer = solve(src)

        capi = driver.find_element(By.CSS_SELECTOR,
            "input.ui-inputfield.ui-inputtext.ui-widget.ui-state-default.ui-corner-all")
        capi.send_keys(answer)
        #Continue Button Click
        driver.find_element(By.CLASS_NAME,"ui-button-text.ui-c")
        time.sleep(1)
        
        #Navigate to the financial information we seek.
        navFin(driver)
        time.sleep(3)
        auditedShow(driver)
        # print("Finished?")
        download(driver,p = directory)

    except (NoAuditedException):
        fins = ["balance","resultado","flujos"]
        for criter in fins:
            finShow(driver,criter)
            time.sleep(1)
            download(driver,p,audit=False,crit = criter)

    except (TimeoutException,ElementNotInteractableException,ElementClickInterceptedException,HTTPError,NoSuchElementException,StaleElementReferenceException) as e:
        print("Something Went Wrong")
        exps.insert(0,used)
        continue
    except (RecursionError,UnexpectedAlertPresentException,PlannedException):
        print("Maximum Recursion exceeded")
        exps.insert(0,used)
        files = os.listdir(f"Financials\\{used}")
        for file in files:
            os.remove(f"Financials\\{used}\\{file}")
    except (KeyboardInterrupt):
        print("Stopping program...")
        files = os.listdir(f"Financials\\{used}")
        for file in files:
            os.remove(f"Financials\\{used}\\{file}")     
        os.rmdir(f"Financials\\{used}") 
        raise KeyboardInterrupt
driver.close()