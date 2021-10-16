import os.path
import requests
import csv
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def create_url(url_base, url_relative):
    return urljoin(url_base, url_relative)

# récupération du titre du livre
def extract_title(soup):
    return soup.find('h1').text.strip()

# Ajoute les livres tant qu'il y a des pages dans la catégorie
def while__category_page(dict_page):
    page = requests.get(dict_page['url'])
    soup = BeautifulSoup(page.content, "html.parser")

    dict_page['title'] = extract_title(soup)
    ol = soup.find('ol')
    hthrees = ol.find_all('h3')
    for hthree in hthrees:
        dict_page['books'].append(create_url(url, hthree.find('a')['href']))

    next = soup.find('ul', class_ = 'pager')
    if next is not None:
        next = next.find('li', class_ = 'next')

    if not next:
        dict_page['next'] = False
    else:
        dict_page['url']= create_url(dict_page['url'], next.find('a')['href'])

# Récupération des livres d'une catégorie
def extract_book_per_category(url):
    result = {
        'url': url,
        'title': '',
        'books': [],
        'next': True
        }
    
    while result['next']:
        while__category_page(result)

    return result

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

# Récupération de la catégorie
def extract_category(soup):
    ul = soup.find('ul', class_='breadcrumb')
    lis = ul.findAll('li')

    return lis[2].text.strip()

# Récupération de la note
def extract_review_rating(soup):
    return soup.find(class_='star-rating')['class'][1]

# Récupération de l'url relative de l'image
def extract_image_url(soup):
    product_gallery = soup.find("div", {"id": "product_gallery"})

    return product_gallery.find('img')['src']

# Récupération des info du livre
def create_info_book(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    result = {}
    result['product_page_url'] = url
    result['title'] = extract_title(soup)
    result['product_description'] = extract_product_description(soup)
    result.update(extract_upc_price_availability(soup))
    result['category'] = extract_category(soup)
    result['review_rating'] = extract_review_rating(soup)
    result['image_url'] = create_url(url, extract_image_url(soup))

    return result

# créé le dossier csv_files et écrit dans un fichier csv les données du dictionnaire
def write_data_books_in_csv(data_list, file_name= 'book'):
    try:
        if not os.path.exists('csv_files'):
            os.makedirs('csv_files')
        with open('csv_files/{}.csv'.format(file_name), 'w', newline='') as csvfile:
            fieldnames = ['product_page_url', 'universal_product_code', 'title', 'price_including_tax', 'price_excluding_tax', 'number_available', 'product_description',
            'category', 'review_rating', 'image_url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for url in data_list:
                data_dict = create_info_book(url)
                writer.writerow({
                    'product_page_url': data_dict['product_page_url'],
                    'title': data_dict['title'],
                    'product_description': data_dict['product_description'],
                    'universal_product_code': data_dict['universal_product_code'],
                    'price_including_tax': data_dict['price_including_tax'],
                    'price_excluding_tax': data_dict['price_excluding_tax'],
                    'number_available': data_dict['number_available'],
                    'category': data_dict['category'],
                    'review_rating': data_dict['review_rating'],
                    'image_url': data_dict['image_url']
                })
    except IOError:
        print('I/O error')

if __name__ == '__main__':
    url = "http://books.toscrape.com/catalogue/category/books/young-adult_21/index.html"
    category = extract_book_per_category(url)
    write_data_books_in_csv(category['books'], category['title'])
