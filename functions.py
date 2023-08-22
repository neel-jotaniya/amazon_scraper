import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

HEADERS = ({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)AppleWebKit/537.36 (KHTML, like Gecko)Chrome/44.0.2403.157 Safari/537.36','Accept-Language': 'en-US, en;q=0.5'})


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

def get_link(soup):
    url = soup.get('href') if soup else None
    return 'https://www.amazon.in/' + url if url else None