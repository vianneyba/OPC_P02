import os.path
import requests
import csv
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

if __name__ == '__main__':
    url = "http://books.toscrape.com/catalogue/its-only-the-himalayas_981/index.html"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    data_dict = {}
    data_dict['product_page_url'] = url
    data_dict['title'] = extract_title(soup)
    data_dict['product_description'] = extract_product_description(soup)
    write_data_books_in_csv(data_dict)
