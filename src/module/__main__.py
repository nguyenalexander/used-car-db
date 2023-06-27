import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import cloudscraper
import extruct
from w3lib.html import get_base_url
import re
import json
import time

def get_webdata():
    # define number of cars per page
    num_cars_pp = 50

    # scrape the first page to get the total number of cars
    url = 'https://www.autotrader.ca/cars/honda/civic/?rcp=' + str(num_cars_pp) + '&rcs=' + str(0) + '&srt=12&prx=-1&loc=L8H%206T8&kwd=si&trans=Manual&hprc=True&wcp=True&sts=New-Used&inMarket=advancedSearch'

    # get total number of cars
    total_num_cars = get_num_cars(url)

    # the number of pages is the total number of cars divided by the cars per page
    num_pages = total_num_cars // num_cars_pp

    # create dictionary with each key as a page
    car_specs_on_pg = dict.fromkeys(range(0, num_pages))

    # loop through the pages
    for page_counter in range(0, num_pages):
        print('================ Page ' + str(page_counter+1) + ' ================')
        url = 'https://www.autotrader.ca/cars/honda/civic/?rcp=' + str(num_cars_pp) + '&rcs=' + str(page_counter * num_cars_pp) + '&srt=12&prx=-1&loc=L8H%206T8&kwd=si&trans=Manual&hprc=True&wcp=True&sts=New-Used&inMarket=advancedSearch'
        car_specs_on_pg[page_counter] = extract_metadata(url)
        time.sleep(60)

    return car_specs_on_pg


def extract_metadata(url):
    all_car_specs = {}
    scraper = cloudscraper.create_scraper()
    info = scraper.get(url)
    base_url = get_base_url(info.text, info.url)
    metadata = extruct.extract(info.text,
                               base_url=base_url,
                               uniform=True,
                               syntaxes=['json-ld',
                                         'microdata',
                                         'opengraph'])
    # loop through the metadata and grab
    for key in metadata:
        if len(metadata[key]) > 0:
            for item in metadata[key]:
                if item['@type'] == 'Product':
                    for car_item in item['offers']['offers']:
                        print(car_item['itemOffered'], ':', car_item['price'])
                        car_url = 'https://www.autotrader.ca' + car_item['url']
                        car_specs = scrape_car_data(car_url)
                        all_car_specs[car_item['url']] = car_specs

    return all_car_specs


def get_num_cars(url):
    scraper = cloudscraper.create_scraper()
    info = scraper.get(url)
    base_url = get_base_url(info.text, info.url)
    metadata = extruct.extract(info.text,
                               base_url=base_url,
                               uniform=True,
                               syntaxes=['json-ld',
                                         'microdata',
                                         'opengraph'])
    num_cars = 0
    for key in metadata:
        if len(metadata[key]) > 0:
            for item in metadata[key]:
                if item['@type'] == 'Product':
                    num_cars = item['offers']['offerCount']

    return num_cars


def scrape_car_data(url):
    # url = "https://www.autotrader.ca/a/honda/civic%20coupe/calgary/alberta/5_58443310_20100115171356763/?showcpo=ShowCpo&ncse=no&ursrc=ts&pc=L8H%206T8&sprx=-1"
    scraper = cloudscraper.create_scraper()
    info = scraper.get(url)
    # TODO: add wait and retry statements in case we get info.response = 403

    soup = BeautifulSoup(info.text, "html.parser")
    soup_jstext_tags = soup.find_all('script', attrs={'type': 'text/javascript'})

    # loop through all the js script tags and get the one with the vehicle specs (where sourcepos==0)
    for car_tag in soup_jstext_tags:
        # TODO: add wait statements in case car_tag.text contains Incapsula incident ID or car_tag == <script src="/_Incapsula_Resource?..." type="text/javascript"></script>
        if car_tag.sourcepos == 0:
            break

    # get string of the 5th tag group (need to fix - remove hardcode?)
    script_tag_contents = car_tag.string

    # get the position where 'specifications' starts
    specs_pos_st = re.search('specs', script_tag_contents)

    # get the position where 'specifications' ends ('showMadeIn' starts)
    specs_pos_end = re.search('showMadeIn', script_tag_contents)

    # get the entire specs string list - possible to do without hardcoding?
    specs_string = script_tag_contents[specs_pos_st.regs[0][1]+2 : specs_pos_end.regs[0][0]-2]

    # json.loads converts the string to a list of dictionaries of key:value pairs, then convert to a dictionary
    specs_dict = {item['key']: item for item in json.loads(specs_string)}
    return specs_dict


def main():
    # conditional to create db or not

    # grab data from webpage
    result = get_webdata()


if __name__ == "__main__":
    main()
