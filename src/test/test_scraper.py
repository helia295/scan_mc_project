import sys
import os
#sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append("/Users/heliadinh/Desktop/Scan_MC_project/Scan_MC_code/src/pycode/scraper/")
from scraper import get_URLs_to_list, getKeywordstoList, get_all_links_on_URL,configure_chrome_driver, findKeyword
import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By


'''
case 1: website url chua https
case 2: ---------------- http

case 1: word trong wordlist co trong found
case 2: ------------------- ko co trong found

case 1: website trong url
case 2: webbsite ko co trong url

'''

def test_get_URLs_to_list_length():
    mc_file = "/Users/heliadinh/Desktop/DS Terminal CTT.csv"
    start_URLs = get_URLs_to_list(mc_file)

    assert len(start_URLs) == 3007

def test_get_URLs_to_list_5first_rows():
    mc_file = "/Users/heliadinh/Desktop/DS Terminal CTT.csv"
    start_URLs = get_URLs_to_list(mc_file)

    assert start_URLs[0:5] == ['https://www.tailoc68.vn/', 
                                'https://portal.evbi.vn/', 
                                'https://vbi.vietinbank.vn/', 
                                'https://orifoodvn.mysapo.net', 
                                'http://www.qrpayshop.vn']

def test_get_Keywords_to_list_length():
    xlsfile = "/Users/heliadinh/Desktop/Keyword.xls"
    wordlist = getKeywordstoList(xlsfile)

    assert len(wordlist) == 110

def test_get_Keywords_to_list_5first_rows():
    xlsfile = "/Users/heliadinh/Desktop/Keyword.xls"
    wordlist = getKeywordstoList(xlsfile)

    assert wordlist[0:5] == ['thẻ điện thoai', 'thẻ game', 'nạp điện thoại', 'thẻ data', 'chiết khấu ']


@pytest.mark.dependency()
def test_configure_chrome_driver():
    driver = configure_chrome_driver()

    assert driver != None


@pytest.mark.dependency(depends=["test_configure_chrome_driver"])
def test_get_all_links_on_URL_length():
    length = 3
    driver = configure_chrome_driver()
    website = "http://songhongcamera.com/"

    driver.get(website)
    WebDriverWait(driver, 15).until(lambda j: j.find_element(by=By.CLASS_NAME, value="container").is_displayed())

    url_list = get_all_links_on_URL(driver, length)

    assert len(url_list) <= length

'''
@pytest.mark.dependency(depends=["test_configure_chrome_driver"])
def test_get_all_links_on_URL_links():
    length = 3
    driver = configure_chrome_driver()
    website = "http://songhongcamera.com/"

    driver.get(website)
    WebDriverWait(driver, 15).until(lambda j: j.find_element(by=By.CLASS_NAME, value="container").is_displayed())

    url_list = get_all_links_on_URL(driver, length)

    assert url_list == ['https://songhongcamera.com/collections/lens-ong-kinh-viltrox', 'https://songhongcamera.vn/#', 'https://goo.gl/maps/VEEZdhGUUFx']
'''

@pytest.mark.dependency(depends=["test_configure_chrome_driver"])
def test_findKeyword_http_url():

    start_URL = "http://songhongcamera.com/"
    wordlist = ["máy ảnh", "ống kính", "cây cối", "sông hồ"] # có, có, ko có, ko có
    driver = configure_chrome_driver()
    num_links = 1
    RELATED_URLS = "/Users/heliadinh/Desktop/scan_MC_project/scan_MC_files/urls/"

    web_dict = findKeyword(driver, start_URL, wordlist, 1, num_links, RELATED_URLS)
    
    assert web_dict == {'STT': 1, 'Website': 'http://songhongcamera.com/', 'Keywords tìm thấy': "['máy ảnh', 'ống kính']", 'Link liên kết ngoài': 'Có', 'Người dùng đăng nhập': 'Có', 'Yêu cầu nạp tiền': 'Có'}


@pytest.mark.dependency(depends=["test_configure_chrome_driver"])
def test_findKeyword_https_url():

    start_URL = "https://dichvucong.binhduong.gov.vn/"
    wordlist = ["dịch vụ", "hành chính", "cây cối", "sông hồ"] # có, có, ko có, ko có
    driver = configure_chrome_driver()
    num_links = 1
    RELATED_URLS = "/Users/heliadinh/Desktop/scan_MC_project/scan_MC_files/urls/"

    web_dict = findKeyword(driver, start_URL, wordlist, 1, num_links, RELATED_URLS)
    
    assert web_dict == {'STT': 1, 'Website': 'https://dichvucong.binhduong.gov.vn/', 'Keywords tìm thấy': "['dịch vụ', 'hành chính']", 'Link liên kết ngoài': 'Không', 'Người dùng đăng nhập': 'Không', 'Yêu cầu nạp tiền': 'Không'}



