import os
import sys
from tracemalloc import start
import csv

from dotenv import dotenv_values

config = dotenv_values("./.env")
RESULT_CSV = config['RESULT_CSV']

from src.pycode.scraper.scraper import get_URLs_to_list, getKeywordstoList, configure_chrome_driver, findKeyword

def main():     
    
    mc_file = sys.argv[1]
    xlsfile = sys.argv[2]
    value = sys.argv[3]
    RELATED_URLS = sys.argv[4]
    

    #dict_list = []
    # Get a list of start URLs to scan
    if "csv" in mc_file: 
        start_URLs = get_URLs_to_list(mc_file)
        os.remove(mc_file)
    else:
        start_URLs = [mc_file]

    f = open(RESULT_CSV, 'w')
    headers = ["STT", "Website", "Keywords tìm thấy", "Link liên kết ngoài", "Người dùng đăng nhập", "Yêu cầu nạp tiền"]
    writer = csv.DictWriter(f, fieldnames = headers)
    writer.writeheader()
    f.flush()
    
    # Get a list of keywords to scan
    wordlist = getKeywordstoList(xlsfile)
    os.remove(xlsfile)

    driver = configure_chrome_driver()
    
    stt = 1
    for web in start_URLs:
        web_dict = findKeyword(driver, web, wordlist, stt, int(value), RELATED_URLS)
        #dict_list.append(web_dict)
        
        writer.writerow(web_dict)
        f.flush()
        stt+=1

    f.close()

main()