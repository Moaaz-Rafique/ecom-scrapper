from email import header
from gettext import gettext
import sys
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import csv
import re
import time
from datetime import datetime

def deEmojify(text):
    regrex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags = re.UNICODE)
    return regrex_pattern.sub(r'',text)

def getPageHtml(url, wait = 0):
    with sync_playwright() as p:
        browser = p.webkit.launch()#headless=False
        page =  browser.new_page()        
        # page.evaluate("() => { document.body.style.zoom=0.25; }")
        page.goto(url)
        # time.sleep(5) #uncomment to if network is slow
        html = page.content()        
        browser.close()
        return html

def findnth(string, substring, n):
    parts = string.split(substring, n + 1)
    if len(parts) <= n + 1:
        return -1
    return len(string) - len(parts[-1]) - len(substring)


base_url = f"https://www.quelquechausse.com"
# long, lat = 24.9227021,67.1200746 # change the longitude  and latitude values
url = f"{base_url}/homme"
print(url)
# sys.exit()
html = getPageHtml(url)
pageSoup = BeautifulSoup(html, features="html.parser")

results_div = pageSoup.find("div", {"class":"list-grid"})
# print(results_div)
records = []
if results_div:
    results_a = results_div.findAll("a")
    print(f"Getting Data for {len(results_a)} stores")
    
    for i in results_a:
        record = dict()
        html = getPageHtml(base_url+i["href"])
        # print(base_url+i["href"])
        res_soup = BeautifulSoup(html, features='html.parser')
        gallery = res_soup.find("div",{"class":"ProductItem-gallery-thumbnails"})
        imageTags = gallery.findAll("img")
        imagesLink = []
        for j in imageTags:
            try:                
                print(j["src"][0:j["src"].find("format")-1])
                imagesLink.append(j["src"][0:j["src"].find("format")-1])
            except Exception as e:
                print(e)
                print("Sheeesh")
        record["url"] = i["href"]        
        records.append(record)
else:     
    print("The link was not loaded properly")
    print("Aborting...")
    sys.exit(1)

# To save the list of records to a csv file

# keys = [
#     'store name',
#     'store type',
#     'store Address',
#     'store website url',
#     'store phone number',
#     'google maps url',
#     'Links for Images of Store',
#     'ExtraData'
# ]
# with open(f'Data_{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.csv', 'w',encoding="utf-8", errors='surrogatepass', newline='') as output_file:
#     dict_writer = csv.DictWriter(output_file, keys)
#     dict_writer.writeheader()
#     dict_writer.writerows(records)


