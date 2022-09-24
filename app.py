from email import header
from gettext import gettext
import sys
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import requests
import csv
import re
import json
import time
from datetime import datetime



def deEmojify(text):
    regrex_pattern = re.compile(pattern="["
                                u"\U0001F600-\U0001F64F"  # emoticons
                                u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                "]+", flags=re.UNICODE)
    return regrex_pattern.sub(r'', text)


def getPageHtml(url, wait=0):
    with sync_playwright() as p:
        browser = p.webkit.launch()  # headless=False
        page = browser.new_page()
        # page.evaluate("() => { document.body.style.zoom=0.25; }")
        page.goto(url)
        time.sleep(wait)  # uncomment to if network is slow
        html = page.content()
        browser.close()
        return html


def findnth(string, substring, n):
    parts = string.split(substring, n + 1)
    if len(parts) <= n + 1:
        return -1
    return len(string) - len(parts[-1]) - len(substring)


keys = [
    "Product ID",
    "Variant ID",
    "Product Type",
    "Product Page",
    "Product URL",
    "Title",
    "Vendor",
    "Description",
    "SKU",
    "Option Name 1",
    "Option Value 1",
    "Option Name 2",
    "Option Value 2",
    "Option Name 3",
    "Option Value 3",
    "Price",
    "Sale Price",
    "On Sale",
    "Stock",
    "Categories",
    "Tags",
    "Weight",
    "Length",
    "Width",
    "Height",
    "Visible",
    "Hosted Image URLs",
]
base_url = f"https://www.quelquechausse.com"
# long, lat = 24.9227021,67.1200746 # change the longitude  and latitude values
records = []
pagesToScrape = ['homme', 'accessoires', 'femmes']
for j in pagesToScrape:
    url = f"{base_url}/{j}"
    print(url)
    # sys.exit()

    # html = requests.get(url).content
    html = getPageHtml(url, wait=5)
    pageSoup = BeautifulSoup(html, features="html.parser")

    results_div = pageSoup.find("div", {"class": "list-grid"})
    # print(results_div)
    if results_div:
        results_a = results_div.findAll("a")
        print(f"Getting Data for {len(results_a)} items in {j} page")

        for i in results_a:
            # html = requests.get(base_url+i["href"]).content
            html = getPageHtml(base_url+i["href"], 3)
            # print(base_url+i["href"])
            res_soup = BeautifulSoup(html, features='html.parser')
            record = dict()
            j = res_soup.find("div", {"class": "product-variants"})

            for key in keys:
                record[key] = ""

            record["Product URL"] = base_url+i["href"]
            try:
                record["Title"] = res_soup.find(
                    "h1", {"class": "ProductItem-details-title"}).getText().strip()
                # record["Vendor"] = ' '.join(record["Title"].split(" ")[0:-1])
                print(record["Title"], record["Vendor"])

            except Exception as e:
                print("Title not loaded")
                print(len(res_soup))
                print(e)
            try:
                record["Description"] = res_soup.find(
                    "div", {"class": "ProductItem-details-excerpt"}).getText().strip()
            except Exception as e:
                print("Description not loaded")
                print(e)

            selectDivs = res_soup.findAll("select")

            try:
                record["Price"] = res_soup.find(
                    "div", {"class": "product-price"}).getText().strip()
            except Exception as e:
                print(e)
                print("Price not loaded")

            gallery = res_soup.find(
                "img", {"class": "ProductItem-gallery-slides-item-image"})
            try:
                record["Hosted Image URLs"] = gallery["data-src"]
            except:
                try:
                    record["Hosted Image URLs"] = gallery["src"]
                except:
                    try:
                        record["Hosted Image URLs"] = gallery["data-image"]
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
            if len(selectDivs) > 0:
                data = json.loads(j["data-variants"])
                # print(data[0])
                for o in data:
                    if o["qtyInStock"] > 0:
                        newRec = record.copy()
                        try:
                            newRec["Option Name 1"] = "Color"
                            newRec["Option Value 1"] = o["attributes"]["Couleur"]
                        except:
                            print("No Color Variants Found")
                        try:
                            newRec["Option Name 2"] = "Size"
                            newRec["Option Value 2"] = o["attributes"]["Taille"]
                        except:
                            print("No size Variants found")
                        records.append(newRec)
            else:
                records.append(record)
    else:
        print("The link was not loaded properly")
        print("Aborting...")
        sys.exit(1)

    # To save the list of records to a csv file


with open(f'Output_{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.csv', 'w', encoding="utf-8-sig", errors='surrogatepass', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(records)
