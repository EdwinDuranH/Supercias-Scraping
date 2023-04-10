from scvs_funcs import *

path = r"C:\Users\eduranh\OneDrive - Universidad San Francisco de Quito\USFQ Online\DataHub\Supercias\Dummy Folder\Edwin\Supercias\Financials"
# path = r"C:\Users\EDWIN\OneDrive - Universidad San Francisco de Quito\USFQ Online\DataHub\Supercias\Financial Information\Financials"
url = "https://appscvsconsultas.supercias.gob.ec/consultaCompanias/societario/busquedaCompanias.jsf"

#Read file with company exps
dframe = pd.read_csv("allexps.csv")
exps = update()[:1000]
len(exps)

used_rucs = []

while len(exps) != 0:
    used = exps.pop(0)
    directory = f"Financials\\{used}"
    if not os.path.isdir(f"Financials\\{used}"):
        os.mkdir(f"Financials\\{used}")       
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs",{"download.default_directory":f"{path}\\{used}",
                                      "download.prompt_for_download":False,
                                      "download.directory_upgrade":True,
                                      "plugins.always_open_pdf_externally":True})
    driver = webdriver.Chrome(options=options)
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
        download(driver,p = directory)
    except (TimeoutException,ElementNotInteractableException,ElementClickInterceptedException,HTTPError,NoSuchElementException,StaleElementReferenceException) as e:
        print("Something Went Wrong")
        exps.insert(0,used)
        continue
    except (RecursionError,UnexpectedAlertPresentException):
        print("Maximum Recursion exceeded")
        exps.insert(0,used)
        files = os.listdir(f"Financials\\{used}")
        for file in files:
            os.remove(f"Financials\\{used}\\{file}")
        continue
driver.close()