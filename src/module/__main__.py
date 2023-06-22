import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import cloudscraper
import extruct
from w3lib.html import get_base_url


def get_webdata():
    num_cars_pp = 15
    output_df = pd.DataFrame([])
    scraper = cloudscraper.create_scraper()
    num_pages = 0
    page_counter = 0
    while num_pages < 100:
        print('================ Page ' + str(page_counter) + ' ================')
        url = 'https://www.autotrader.ca/cars/honda/civic/?rcp=' + str(num_cars_pp) + '&rcs=' + str(page_counter * num_cars_pp) + '&srt=12&prx=-1&loc=L8H%206T8&kwd=si&trans=Manual&hprc=True&wcp=True&sts=New-Used&inMarket=advancedSearch'
        info = scraper.get(url)

        base_url = get_base_url(info.text, info.url)
        metadata = extruct.extract(info.text,
                                   base_url=base_url,
                                   uniform=True,
                                   syntaxes=['json-ld',
                                             'microdata',
                                             'opengraph'])
        # soup = BeautifulSoup(info.text, "html.parser")
        # soup_text = soup.get_text()
        # soup_script_tags = soup.find_all('script')
        # soup_script_app_json_tags = soup.find_all('script', type='application/ld+json')

        for key in metadata:
            if len(metadata[key]) > 0:
                for item in metadata[key]:
                    if item['@type'] == 'Product':
                        num_cars = item['offers']['offerCount']
                        num_pages = num_cars / num_cars_pp
                        for car_item in item['offers']['offers']:
                            print(car_item['itemOffered'], ':', car_item['price'])
                            print('https://www.autotrader.ca' + car_item['url'])


        page_counter += 1
        if page_counter > num_pages:
            break
    return output_df


def main():
    # conditional to create db or not

    # grab data from webpage
    used_car_data_df = get_webdata()


if __name__ == "__main__":
    main()
