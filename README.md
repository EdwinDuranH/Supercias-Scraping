### Scraper for the Supercias Database

The objective of this script is to scrape the website from the Superintendencia de Compañías. The language used is Python, and the library used is Selenium. The objective is to extract all of the audited financial statements available for the companies listed on the platform. If there are no audited financials for a company, the program is designed to download the regular financial statements. A list of expedientes, an identifier number for the company, must be provided in the form of a csv file in order for the program to look for those companies automatically.

There are two main code files. The first one is scvs_funcs.py which has all the methods needed for the program to scrape the website. The second one is fin_extract.py which provides the structure for the scraping and uses these methods in an orderly function. It is in charge of generating the directories per company and to catch any exceptions that might occur during the scraping process, including recursion depth errors, server connection errors, and small errors that happen because of how the Superintendencia's website works.

#### Additional information

There are captchas inside this website. They pop up in a very high frequency, and they do at random, per every interaction with any element inside the website. Fortunately, they are extremely simple: They are just a series of numbers that are well formatted and use the same font. Therefore it's easy to solve them using OCR. The solve() and solve_other() functions are designed to do this shall a captcha pop up at any time.

The server has usual maintenances every month. This renders the website almost unusable by a machine, as it becomes very buggy, and it fails to load elements correctly. It is advised to stop using the script in case the website is behaving weirdly. Further work is in progress to control for this issue, but so far it is not robust to deficient element loading because of server maintenance.