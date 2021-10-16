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
    except IOError:
        print('I/O error')

if __name__ == '__main__':
    url = "http://books.toscrape.com/catalogue/its-only-the-himalayas_981/index.html"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    data_dict = {}

    write_data_books_in_csv(data_dict)
