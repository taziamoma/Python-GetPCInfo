from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import chromedriver_autoinstaller
chromedriver_autoinstaller.install()

from selenium.webdriver.support.wait import WebDriverWait

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')

PATH = "C:\Program Files (x86)\chromedriver.exe"
driver = webdriver.Chrome(PATH, options=chrome_options)

def getDellName(tag):
    url = "https://www.dell.com/support/search/en-us#q={}".format(tag)

    driver.get(url)
    wait = WebDriverWait(driver, 7)
    wait.until(lambda driver: driver.current_url != url)

    title = driver.title.replace("Support for ", "").replace(" | Overview | Dell US", "")
    if (title != "Search Support | Dell US"):
        return title
    else:
        return "None"

def getHPName(tag):
    url = "https://support.hp.com/us-en"
    driver.get(url)
    wait = WebDriverWait(driver, 5)

    textbox_id = "searchQueryField"

    search = driver.find_element_by_id(textbox_id)

    search.send_keys(tag)
    search.send_keys(Keys.RETURN)
    wait.until(lambda driver: driver.current_url != url)

    title = driver.title.replace(" (ENERGY STAR) | HP® Customer Support", "").replace(" Desktop PC | HP® Customer Support", "")
    if "| HP® Customer Support" not in title:

        return title
    else:
        return "None"

    #return title


#print(getDellName("9G4NQ22"))
print(getHPName("CNF7133MPG"))