import requests
from bs4 import BeautifulSoup
import os 
import pandas as pd
import re 

HEADERS = ({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)AppleWebKit/537.36 (KHTML, like Gecko)Chrome/44.0.2403.157 Safari/537.36','Accept-Language': 'en-US, en;q=0.5'})
URL = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1"

class DataHandler:
    def __init__(self, data=None):
        if data:
            self.dataframe = pd.DataFrame([data], index=[0])
        else:
            self.dataframe = pd.DataFrame()
        
    
    def __add__(self, other):
        new_handler = DataHandler()
        new_handler.dataframe = pd.concat([self.dataframe, other.dataframe], ignore_index=True)
        return new_handler
    
    def save(self, filename):
        if os.path.isfile(filename):
            existing_data = pd.read_excel(filename)
            updated_data = pd.concat([existing_data, self.dataframe], ignore_index=True)
            updated_data.to_excel(filename, index=False)   
        else:   
            self.dataframe.to_excel(filename, index=False)
    
def make_soup(url):
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.content, features='html5lib')
    return soup  

def get_review(url):
    soup = make_soup(url)
    review_string = soup.find('div', attrs={'data-hook':'cr-filter-info-review-rating-count'})
    if review_string:
        review_string = review_string.text.strip()
        pattern = r"(\d+)\swith\sreviews"
        review = re.search(pattern, review_string)
        if review:
            return review.group(1)
        return -1

def scrape_other_detail(data):
    soup = make_soup(data['Product url'])
    description = ""
    asin = ""
    manufacturer = ""
    description_points = soup.find_all('li', attrs={'class':'a-spacing-mini'})
    for point in description_points:
        description += point.text
    
    product_details_list = soup.find('ul', attrs={'class':'a-unordered-list a-nostyle a-vertical a-spacing-none detail-bullet-list'})
    if product_details_list:
        for detail in product_details_list.find_all('li'):
            # print(detail.text)
            main_span = detail.find('span', attrs={'class':'a-list-item'})
            spans = main_span.find_all('span')
            if not spans or (spans and len(spans) < 2):
                continue
            s1 = spans[0]
            s2 = spans[1]
            if s1.text.startswith('ASIN'):
                asin = s2.text
            elif s1.text.startswith('Manufacturer'):
                manufacturer = s2.text
        
    else:
        product_details = soup.find_all('table', attrs={'class':'a-keyvalue prodDetTable'})
        for table in product_details:
            for tr in table.find_all('tr'):
                th = tr.find('th')
                if th.text.strip() == 'Manufacturer':
                    td = tr.find('td')
                    manufacturer = td.text
                if th.text.strip() == 'ASIN':
                    td = tr.find('td')
                    asin = td.text.strip()
    review_link = soup.find('a', attrs={'data-hook':'see-all-reviews-link-foot'})
    review = get_review('https://www.amazon.in/' + review_link.get('href')) if review_link else None
    data['Description'] = description
    data['ASIN'] = asin
    data['Manufacturer'] = manufacturer
    data['Review'] = review if review != -1 else "NAN"
    
           
            
                
data_model = DataHandler()

for i in range(1):
    soup = make_soup(URL)
    sponserd='sg-col-20-of-24 s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 AdHolder sg-col s-widget-spacing-small sg-col-12-of-16'
    normal = 'sg-col-20-of-24 s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col s-widget-spacing-small sg-col-12-of-16'
    products = soup.find_all('div', attrs={'class':normal})
    print(len(products))
    for product in products:
        price = product.find('span', attrs={'class':'a-offscreen'})
        name = product.find('span', attrs={'class':'a-size-medium a-color-base a-text-normal'})
        url = product.find('a', attrs={'class':'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'})
        next_page_url = soup.find('a', attrs={'class':'s-pagination-item s-pagination-next s-pagination-button s-pagination-separator'})
        rating = product.find('span', attrs={'class':'a-size-base puis-normal-weight-text'})
        
        data = {
            'Name':name.text,
            'Price':price.text,
            'Rating':rating.text if rating else None,
            'Product url':'https://www.amazon.in/' + url.get('href'),
        }
        scrape_other_detail(data)
        data_model += DataHandler(data)
        URL = 'https://www.amazon.in/' + next_page_url.get('href')
        
    print("*"*50)
    print(len(products))
data_model.save('sample.xlsx')


# scrape_other_detail({'Product url':'https://www.amazon.in/Skybags-Brat-Black-Casual-Backpack/dp/B08Z1HHHTD/ref=sr_1_3?crid=2M096C61O4MLT&keywords=bags&qid=1692716718&sprefix=ba%2Caps%2C283&sr=8-3'})

# a = get_review('https://www.amazon.in/Promate-Messenger-Water-Resistant-Detachable-Anti-Theft/product-reviews/B07FDXXL2L/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews')
# print(a)