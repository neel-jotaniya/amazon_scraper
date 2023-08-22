from functions import DataHandler, make_soup, get_link
import re 
global URL
def get_review(url, data):
    soup = make_soup(url)
    review_string = soup.find('div', attrs={'data-hook':'cr-filter-info-review-rating-count'})
    review_string = review_string.text.strip()
    pattern = r"(\d+)\swith\sreviews"
    review = re.search(pattern, review_string)
    rating_str = soup.find('div', attrs={'data-hook':'rating-out-of-text'})
    if rating_str:
        rating = rating_str.text.strip().split()[0]
        data['Rating'] = rating if data['Rating'] != None else None
    data['Review'] = review if review else None
    
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
    get_review(get_link(review_link), data)
    data['Description'] = description
    data['ASIN'] = asin
    data['Manufacturer'] = manufacturer
    
    
def run(url, number_of_pages, filename, include_sponserd=False):       
    main_url = url
    data_model = DataHandler()
    for i in range(number_of_pages):
        soup = make_soup(main_url)
        # sponserd ='sg-col-20-of-24 s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 AdHolder sg-col s-widget-spacing-small sg-col-12-of-16'
        normal = 'sg-col-20-of-24 s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col s-widget-spacing-small sg-col-12-of-16'
        products = soup.find_all('div', attrs={'class':normal}) 
        # sponserd_products = soup.find_all('div', attrs={'class':sponserd}) 
        # all_products = products + sponserd_products if include_sponserd else products
        print(len(products))
        # print(len(sponserd_products))
        next_page_url = soup.find('a', attrs={'class':'s-pagination-item s-pagination-next s-pagination-button s-pagination-separator'})
            
        for product in products:
            main_url = 'https://www.amazon.in/' + next_page_url.get('href')

            # try:
            price = product.find('span', attrs={'class':'a-offscreen'})
            name = product.find('span', attrs={'class':'a-size-medium a-color-base a-text-normal'})
            product_url = product.find('a', attrs={'class':'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'})
            rating = product.find('span', attrs={'class':'a-size-base puis-normal-weight-text'})
            data = {
                'Name':name.text,
                'Price':price.text,
                'Rating':rating.text if rating else None,
                'Product url':'https://www.amazon.in/' + product_url.get('href'),
            }
            scrape_other_detail(data)
            data_model += DataHandler(data)
            print("Product scraped: ", name.text)
            # except:
            #     pass
        print(f"Page {i+1} scraped")
    data_model.save(filename)
    
if __name__=='__main__':
    url = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1"
    run(url, 2, 'data.xlsx')

