from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import re
from pandas import *
import csv
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import threading

#MAX_LINKS = 5     # max follow links per merchant
#DRIVER_PATH="./config/chromedriver"

### Read data from CSV to get merchants' URLs
def get_URLs_to_list(filename):
    url_list = []
    file = open(filename, encoding="utf8")
    csvreader = csv.reader(file)

    next(csvreader)
    for row in csvreader:
        web = row[3]
        if (web != "NULL"):
            if web not in url_list:
                url_list.append(web)

    return url_list

### Read data from file excel Keyword into a dictionary (key: Linh vuc kinh doanh; values: keywords)
def getKeywordstoList(xlsfile):
    xls = ExcelFile(xlsfile)
    df = xls.parse(xls.sheet_names[0]).to_dict()

    wordList = []
    for d in df.values():
        for word in d.values():
            if "nan" not in str(word):
                wordList.append(word)
    return wordList


def get_all_links_on_URL(driver, num_links):
    ### Get all inner links on html page va insert main link vao dau
    all_links = driver.find_elements(by=By.XPATH, value="//a[@href]")
    url_list = []
    for url in all_links:
        url = url.get_attribute("href")
        if ("http" in url) and (url not in url_list):
            url_list.append(url)
        if len(url_list) == num_links:
            break
    return url_list


threadLocal = threading.local()

# configure Chrome Webdriver
def configure_chrome_driver():
    
    # Add additional Options to the webdriver
    options = Options()
    
    # add the argument and make the browser Headless.
    options.add_argument("--headless")
    options.add_argument('--no-sandbox')

    # Instantiate the Webdriver: Mention the executable path of the webdriver you have downloaded
    # if driver is in PATH, no need to provide executable_path
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    return driver


def findKeyword(driver, website, wordlist, stt, num_links, related_urls):
    
    external_links = False
    user_login = False
    nap_tien = False
    domain = ""
    if "https://" in website:
        domain = (website.replace("https://", "")).split("/")[0]
    elif "http://" in website:
        domain = (website.replace("http://", "")).split("/")[0]
    domain = domain.replace(".", "")
    domain = domain.replace("www", "")
    f = open(f"{related_urls}{domain}.csv", 'w')

    web_dict = {}
    web_dict["STT"] = stt
    web_dict["Website"] = website

    try:
        driver.get(website)
    except:
        print("Không reach được website " + website + "\n")
        f.write("Không reach được website " + website + "\n")
        web_dict["Keywords tìm thấy"] = "'N/A'"
        web_dict["Link liên kết ngoài"] = "'N/A'"
        web_dict["Người dùng đăng nhập"] = "'N/A'"
        web_dict["Yêu cầu nạp tiền"] = "'N/A'"

        return web_dict

    try:
        WebDriverWait(driver, 15).until(
            lambda s: s.find_element(by=By.CLASS_NAME, value="content").is_displayed())
    except:
        try:
            WebDriverWait(driver, 15).until(
                lambda r: r.find_element(by=By.ID, value="content").is_displayed())
        except:
            try:
                WebDriverWait(driver, 15).until(
                    lambda j: j.find_element(by=By.CLASS_NAME, value="container").is_displayed())
            except:
                driver.implicitly_wait(30)

    soup = BeautifulSoup(driver.page_source, "lxml")
    #print(soup.prettify())

    # Get all inner links on html page va insert main link vao dau
    url_list = get_all_links_on_URL(driver, num_links)
    url_list.insert(0, website)

    seen = []   # to avoid visiting duplicate urls
    found = []     # to avoid scanning already found words
    seen_domain = []    # to avoid seen domain
    ### Collect all scanned external urls to csv file 
    
    f.write("Những website liên kết với " + website + "\n")
    for url in url_list:
        if url not in seen:
            #print("Scanning " + url)
            if url != website:
                try:
                    driver.get(url)
                except:
                    continue
                try:
                    WebDriverWait(driver, 10).until(
                        lambda s: s.find_element(by=By.CLASS_NAME, value="content").is_displayed())
                except:
                    try:
                        WebDriverWait(driver, 10).until(
                            lambda r: r.find_element(by=By.ID, value="content").is_displayed())
                    except:
                        try:
                            WebDriverWait(driver, 10).until(
                                lambda j: j.find_element(by=By.CLASS_NAME, value="container").is_displayed())
                        except:
                            driver.implicitly_wait(20)
                soup = BeautifulSoup(driver.page_source, "lxml")

                ### Add more hyperlinks from opening new links on main page until reach MAX
                if len(url_list) < num_links:
                    new_urls = get_all_links_on_URL(driver, num_links)
                    for u in new_urls:
                        if (u not in url_list) and (len(url_list) < num_links):
                            url_list.append(u)
                        if len(url_list) == num_links:
                            break
                #print(soup.prettify())
            
            ### Check if User Login is required
            login_match1 = re.search("Đăng nhập", str(soup))
            login_match2 = re.search("Mật khẩu", str(soup))
            if (login_match1 != None) or (login_match2 != None):
                user_login = True

            ### Check if Nap tien is required
            vi_match1 = re.search("Nạp tiền vào ví", str(soup))
            vi_match2 = re.search("số dư ví", str(soup))
            if (vi_match1 != None) or (vi_match2 != None):
                nap_tien = True
            
            ### Scan keywords
            for word in wordlist:
                if word not in found:
                    #print("Searching for " + word)
                    match = re.search((" " + word + " "), str(soup))
                    if match != None:
                        print("Tìm thấy " + word + " trên " + website + " với context \"" + (str(soup))[(match.start()-5):(match.end()+5)] + "\";\n")
                        found.append(word)

                        # Check if Nap tien is required
                        if word == "nạp tiền":
                            nap_tien = True
            seen.append(url)

            if (str(website) not in url) and ("google" not in url) and (".css" not in url) and (".js" not in url):
                if "https://" in url:
                    dom = (url.replace("https://", "")).split("/")[0]
                    if dom not in seen_domain:
                        f.write(dom + '\n')
                        seen_domain.append(dom)
                        external_links = True
                elif ("http://" in url) and ("https://" not in url):
                    dom = (url.replace("http://", "")).split("/")[0]
                    if dom not in seen_domain:
                        f.write(dom + '\n')
                        seen_domain.append(dom)
                        external_links = True
            if "login" in url:
                user_login = True
    f.close()

    ### Result
    if found == []:
        print("Không tìm thấy keyword nào trên " + website + ".\n")
    
    web_dict["Keywords tìm thấy"] = str(found)
    if external_links == True:
        web_dict["Link liên kết ngoài"] = "Có"
    else:
        web_dict["Link liên kết ngoài"] = "Không"
    if user_login == True:
        web_dict["Người dùng đăng nhập"] = "Có"
    else:
        web_dict["Người dùng đăng nhập"] = "Không"
    if user_login == True:
        web_dict["Yêu cầu nạp tiền"] = "Có"
    else:
        web_dict["Yêu cầu nạp tiền"] = "Không"

    return web_dict
        
'''         
def main():
    
    filename = "DS Terminal CTT.csv"
    start_URLs = get_URLs_to_list(filename)

    # Get a list of keywords to scan
    xlsfile = 'Keyword.xls'
    wordlist = getKeywordstoList(xlsfile)

    driver = configure_chrome_driver()

    dict_list = []
    stt = 18
    for web in start_URLs[20:30]:
        web_dict = findKeyword(driver, web, wordlist, stt)
        if web_dict != {}:
            dict_list.append(web_dict)
            stt+=1

    
    headers = ["Website", "Keywords tìm thấy", "Link liên kết ngoài", "Người dùng đăng nhập", "Yêu cầu nạp tiền"]

    with open('./results/result2.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = headers)
        writer.writeheader()
        writer.writerows(dict_list)
    

    # close the driver.
    driver.quit()

main()'''