import os.path
import requests
import csv
import re
from bs4 import BeautifulSoup


# créé le dossier csv_files et écrit dans un fichier csv les données du dictionnaire
def write_data_books_in_csv(data_dict, file_name= 'book'):
    try:
        if not os.path.exists('csv_files'):
            os.makedirs('csv_files')
        with open('csv_files/{}.csv'.format(file_name), 'w', newline='') as csvfile:
            fieldnames = ['product_page_url', 'universal_product_code', 'title', 'price_including_tax', 'price_excluding_tax', 'number_available', 'product_description',
            'category', 'review_rating', 'image_url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({
                'product_page_url': data_dict['product_page_url'],
                'title': data_dict['title'],
                'product_description': data_dict['product_description'],
                'universal_product_code': data_dict['universal_product_code'],
                'price_including_tax': data_dict['price_including_tax'],
                'price_excluding_tax': data_dict['price_excluding_tax'],
                'number_available': data_dict['number_available'],
            })
    except IOError:
        print('I/O error')

# récupération du titre du livre
def extract_title(soup):
    return soup.find('h1').text.strip()

# Récupération de la description grâce aux Métadonnées
def extract_product_description(soup):
    product_description = soup.find('meta', {'name': 'description'})
    product_description = product_description['content'].strip()

    return product_description

# Récupération upc, des prix, et de la disponibilité
def extract_upc_price_availability(soup):
    result = {}
    product_table_info = soup.find('table', class_="table table-striped")
    trs = product_table_info.find_all('tr')
    for tr in trs:
        th = tr.find('th')
        if th.text == 'UPC':
            result['universal_product_code'] = tr.find('td').text.strip()
        elif th.text == 'Price (excl. tax)':
            result['price_excluding_tax'] = tr.find('td').text.strip()
        elif th.text == 'Price (incl. tax)':
            result['price_including_tax'] = tr.find('td').text.strip()
        elif th.text == 'Availability':
            quantities = re.search('([0-9]{1,})', tr.find('td').text.strip())
            result['number_available'] = quantities[0]

    return result

if __name__ == '__main__':
    url = "http://books.toscrape.com/catalogue/its-only-the-himalayas_981/index.html"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    data_dict = {}
    data_dict['product_page_url'] = url
    data_dict['title'] = extract_title(soup)
    data_dict['product_description'] = extract_product_description(soup)
    data_dict.update(extract_upc_price_availability(soup))
    write_data_books_in_csv(data_dict)
