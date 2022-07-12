import os
import sys
from tracemalloc import start
import csv
from multiprocessing.pool import ThreadPool
import itertools
import threading
import gc

from dotenv import dotenv_values

config = dotenv_values("./.env")
RESULT_CSV = config['RESULT_CSV']
THREADS_COUNT = int(config['THREADS_COUNT'])

from src.pycode.scraper.scraper import get_URLs_to_list, getKeywordstoList, findKeyword

def main():     

    mc_file = sys.argv[1]
    xlsfile = sys.argv[2]
    value = sys.argv[3]
    RELATED_URLS = sys.argv[4]
    
    # Get a list of start URLs to scan
    if "csv" in mc_file: 
        start_URLs = get_URLs_to_list(mc_file)
        os.remove(mc_file)
    else:
        start_URLs = [mc_file]

    f = open(RESULT_CSV, 'w', encoding="utf8")
    headers = ["Website", "Keywords tìm thấy", "Link liên kết ngoài", "Người dùng đăng nhập", "Yêu cầu nạp tiền"]
    writer = csv.DictWriter(f, fieldnames = headers)
    writer.writeheader()
    f.flush()
    
    # Get a list of keywords to scan
    wordlist = getKeywordstoList(xlsfile)
    os.remove(xlsfile)

    threadLocal = threading.local()

    with ThreadPool(THREADS_COUNT) as pool:
        res = list(pool.starmap(findKeyword, [*zip(start_URLs, itertools.repeat(wordlist), itertools.repeat(int(value)), itertools.repeat(RELATED_URLS), itertools.repeat(writer), itertools.repeat(f), itertools.repeat(threadLocal))]))
        # must be done before terminate is explicitly or implicitly called on the pool:
        del threadLocal
        gc.collect()

    pool.terminate()

    f.close()

main()