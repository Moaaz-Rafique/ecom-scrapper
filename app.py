from email import header
from gettext import gettext
import sys
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import requests
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
records = []
pagesToScrape = ['homme', 'accessoires', 'femmes']
for i in ['homme', 'accessoires', 'femmes']:
    url = f"{base_url}/{i}"
    print(url)
    # sys.exit()
    html = requests.get(url).content
    html = getPageHtml(url)
    pageSoup = BeautifulSoup(html, features="html.parser")

    results_div = pageSoup.find("div", {"class":"list-grid"})
    # print(results_div)
    if results_div:
        results_a = results_div.findAll("a")
        print(f"Getting Data for {len(results_a)} items in {i} page")
        
        for i in results_a:

            html = requests.get(base_url+i["href"]).content
            html = getPageHtml(base_url+i["href"])
            print(base_url+i["href"])
            res_soup = BeautifulSoup(html, features='html.parser')
            record = dict()
            record["Product ID"]=""
            record["Variant ID"]=""
            record["Product Type"]=""
            record["Product Page"]=""
            record["Product URL"]=base_url+i["href"]
            try:            
                record["Title"]=res_soup.find("h1", {"class":"ProductItem-details-title"}).getText()
            except Exception as e:
                print(e)
                print("Title not loaded")
            try:    
                record["Description"]=res_soup.find("div", {"class":"ProductItem-details-excerpt"}).getText()
            except Exception as e:
                print(e)
                print("Description not loaded")    
            record["SKU"]=""
            selectDivs = res_soup.findAll("select")
            record["Option Name 2"]=""
            record["Option Value 2"]=""

            record["Option Name 3"]=""
            record["Option Value 3"]=""
            for i in range(len(selectDivs)):
                select = selectDivs[i]
                record[f"Option Name {i+1}"]=select["data-variant-option-name"]
                record[f"Option Value {i+1}"]=select["aria-label"]


            try:
                record["Price"]=res_soup.find("div", {"class":"product-price"}).getText()
            except Exception as e:
                print(e)
                print("Price not loaded")
            record["Sale Price"]=""
            record["On Sale"]=""
            record["Stock"]=""

            record["Categories"]=i

            record["Tags"]=""

            record["Weight"]=""
            record["Length"]=""
            record["Width"]=""
            record["Height"]=""

            gallery = res_soup.find("img",{"class":"ProductItem-gallery-slides-item-image"})
            try:
                record["Visible	Hosted Image URLs"]=gallery["data-src"]
            except:
                try:
                    record["Visible	Hosted Image URLs"]=gallery["src"]
                except:
                    try:
                        record["Visible	Hosted Image URLs"]=gallery["data-image"]                
                    except Exception as e:
                        print(e)
                        print("Image link not loaded")
                
            # if gallery:
            #     imageTags = gallery.findAll("img")
            #     imagesLink = []
                

            #     title = res_soup.find("h1", {"class":"ProductItem-details-title"})
            #     price = res_soup.find("div", {"class":"product-price"})
            #     # som = res_soup.find("div", {"class":"product-price"})
            #     for j in imageTags:
            #         try:                
            #             # print(j["src"][0:j["src"].find("format")-1])
            #             print(j)
            #             imagesLink.append(j["data-src"][0:j["data-src"].find("format")-1])
            #         except Exception as e:
            #             print(e)
            #             # print("Sheeesh")
            # else:
            #     print(gallery) 
            # record["url"] = i["href"]        
            records.append(record)
    else:     
        print("The link was not loaded properly")
        print("Aborting...")
        sys.exit(1)

    # To save the list of records to a csv file




keys = records[0].keys()
with open(f'Output_{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.csv', 'w',encoding="utf-8", errors='surrogatepass', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(records)