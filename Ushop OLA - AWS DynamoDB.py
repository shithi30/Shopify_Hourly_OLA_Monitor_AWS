#!/usr/bin/env python
# coding: utf-8

# import
from pyvirtualdisplay import Display
import chromedriver_autoinstaller
from selenium import webdriver
from bs4 import BeautifulSoup
import os
import boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
import time

# session
dynamo_resource = boto3.resource (
    service_name = "dynamodb", 
    region_name = "ca-central-1", 
    aws_access_key_id = os.getenv("AWS_ACC"), 
    aws_secret_access_key = os.getenv("AWS_SEC")
)

# table
ushop_tbl = dynamo_resource.Table("ushop_ola")
print(ushop_tbl.table_status)

# setup
Display(visible = 0, size = (1920, 1080)).start() 
options = webdriver.ChromeOptions()

# pref.
options.add_argument("ignore-certificate-errors")
options.add_argument("headless")

# open window
driver = webdriver.Chrome(options = options)
driver.maximize_window()

# init.
pg = 0
skus = []
report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
expiry_time = int(time.time()) + 7*24*3600

# link
while(1): 
    pg = pg + 1
    link = "https://ushopbd.com/collections/all?page=" + str(pg) + "&view=list"
    driver.get(link)

    # soup
    soup_init = BeautifulSoup(driver.page_source, "html.parser")
    soup = soup_init.find_all("div", attrs = {"class": "list-view-item__title-column"})

    # page
    sku_count = len(soup)
    if sku_count == 0: break 
    print("Scraping from page: " + str(pg))
    
    # scrape
    for i in range(0, sku_count):
        record = {}
        
        # SKU
        try: record["sku"] = sku = soup[i].find("div", attrs = {"class": "h4 grid-view-item__title"}).get_text()
        except: pass
        # current price
        try: record["current_price"] = soup[i].find("span", attrs = {"class": "money"}).get_text()[3:]
        except: pass
        # original price
        try: record["original_price"] = soup[i].find("s", attrs = {"class": "product-price__price"}).get_text()[3:]
        except: pass        
        # previous status
        if_exists = 1
        try: sku = ushop_tbl.get_item(Key = {"sku": sku})["Item"]["sku"]
        except: if_exists = 0
        if if_exists == 1: record["previous_ola"], record["report_time"] =  True, report_time
        if if_exists == 0: record["previous_ola"], record["report_time"] = False, report_time
        # TTL
        record["expiry_time"] = expiry_time

        # put
        skus.append(sku)
        ushop_tbl.put_item(Item = record)

# close window
driver.close()

# mark EOF
ushop_tbl.put_item(Item = {"sku": "EOF", "report_time": report_time})

# stats
print("Live SKUs found: " + str(len(skus)))
print("Data pulled at: " + report_time)


