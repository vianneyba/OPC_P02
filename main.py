import os.path
import requests
import csv
import re
import sys
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def extract_soup(link):
    page = requests.get(link)
    return BeautifulSoup(page.content, "html.parser")

def create_url(url_base, url_relative):
    return urljoin(url_base, url_relative)

def extract_title(soup):
    """ Récupération du titre du livre
        Parameters:
            soup: bs4.BeautifulSoup
        Returns:
            String
    """
    return soup.find('h1').text.strip()

def while_category_page(dict_page):
    """ Ajoute les livres tant qu'il y a des pages dans la catégorie et ajoute le 'title' dans le dictionnaire en entrée.
        Parameters:
            dict: 
                {   
                    'url': 'http://books.toscrape.com/catalogue/category/books/travel_2/index.html',
                    'title': '',
                    'books': [],
                    'next': True
                }
        Returns:

    """
    soup= extract_soup(dict_page['url'])

    dict_page['title'] = extract_title(soup)
    ol = soup.find('ol')
    hthrees = ol.find_all('h3')
    for hthree in hthrees:
        dict_page['books'].append(create_url(dict_page['url'], hthree.find('a')['href']))

    next = soup.find('ul', class_ = 'pager')
    if next is not None:
        next = next.find('li', class_ = 'next')

    if not next:
        dict_page['next'] = False
    else:
        dict_page['url']= create_url(dict_page['url'], next.find('a')['href'])

def extract_book_per_category(url):
    """ Récupération des livres d'une catégorie
        Parameters:
            str
        Returns:
            dict
    """
    result = {
        'url': url,
        'title': '',
        'books': [],
        'next': True
        }
    
    while result['next']:
        while_category_page(result)
    return result

def extract_category_url(url):
    """ Récupération d'une des catégories du site.
        Parameters:
            str
        Returns:
            list:
                [
                    {
                        'title': 'Travel',
                        'url': 'http://books.toscrape.com/catalogue/category/books/travel_2/index.html'
                    },
                    {
                        'title': 'Mystery',
                        'url': 'http://books.toscrape.com/catalogue/category/books/mystery_3/index.html'
                    }
                ]
    """
    soup= extract_soup(url)
    
    url_categories = []
    nav_list = soup.find('ul', class_='nav nav-list')
    lis = nav_list.find_all('li')
    lis.pop(0)
    for li in lis:
        dic_category = {
            'title': li.text.strip(),
            'url': create_url(url, li.find('a')['href'])
        } 
        url_categories.append(dic_category)
    return url_categories

def extract_product_description(soup):
    """ Récupération de la description grâce aux Métadonnées.
        Parameters:
            soup: bs4.BeautifulSoup
        Returns:
            str
    """
    product_description = soup.find('meta', {'name': 'description'})
    product_description = product_description['content'].strip()

    return product_description

def extract_upc_price_availability(soup):
    """ Récupération upc, des prix, et de la disponibilité.
        Parameters:
            soup: bs4.BeautifulSoup
        Returns:
            dict
                {
                    'universal_product_code': '3bc89353f7e3a3cc',
                    'price_excluding_tax': '£54.21',
                    'price_including_tax': '£54.21',
                    'number_available':
                    '14'
                }
    """
    result = {'number_available': 0}
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

def extract_category(soup):
    """ Récupération de la catégorie
        Parameters:
            soup: bs4.BeautifulSoup
        Returns:
            str
    """
    ul = soup.find('ul', class_='breadcrumb')
    lis = ul.findAll('li')
    return lis[2].text.strip()

def extract_review_rating(soup):
    """ Récupération de la note
        Parameters:
            soup: bs4.BeautifulSoup
        Returns:
            str
    """
    return soup.find(class_='star-rating')['class'][1]

def extract_image_url(soup):
    """ Récupération de l'url relative de l'image
        Parameters:
            soup: bs4.BeautifulSoup
        Returns:
            str
    """
    product_gallery = soup.find('div', {'id': 'product_gallery'})

    return product_gallery.find('img')['src']

def create_info_book(url):
    """ Récupération des informations du livre
        Parameters:
            url: str
        Returns:
            dict:
                {
                    'product_page_url': 'http://books.toscrape.com/catalogue/the-great-railway-bazaar_446/index.html',
                    'title': 'The Great Railway Bazaar',
                    'product_description': "First publishedtial ...more",
                    'universal_product_code': '48736df57e7bec9f',
                    'price_excluding_tax': '£30.54',
                    'price_including_tax': '£30.54',
                    'number_available': '6',
                    'category': 'Travel',
                    'review_rating': 'One',
                    'image_url': 'http://books.toscrape.com/media/cache/d5/82/d582f6b0261c2842330e893962276295.jpg'
                }
    """
    soup= extract_soup(url)

    result = {}
    result['product_page_url'] = url
    result['title'] = extract_title(soup)
    result['product_description'] = extract_product_description(soup)
    result.update(extract_upc_price_availability(soup))
    result['category'] = extract_category(soup)
    result['review_rating'] = extract_review_rating(soup)
    result['image_url'] = create_url(url, extract_image_url(soup))
    return result

def extract_image(image_url):
    """ Enregistrement local du fichier image
        Parameters:
            image_url: str
    """
    img_data = requests.get(image_url).content
    pr = urlparse(image_url)
    with open('images/'+os.path.basename(pr.path), 'wb') as handler:
        handler.write(img_data)

def write_data_books_in_csv(data_list, file_name= 'book', pagination= None, with_image= True):
    """ Créé le dossier csv_files, images et écrit dans un fichier csv les données du dictionnaire
    """
    print('{}/{} Catégorie : {} ({} livre(s))'.format(pagination['current_category'], pagination['nb_category'], file_name, pagination['nb_book']))
    try:
        if not os.path.exists('csv_files'):
            os.makedirs('csv_files')
        if not os.path.exists('images'):
            os.makedirs('images')
        with open('csv_files/{}.csv'.format(file_name), 'w', newline='') as csvfile:
            fieldnames = ['product_page_url', 'universal_product_code', 'title', 'price_including_tax', 'price_excluding_tax', 'number_available', 'product_description',
            'category', 'review_rating', 'image_url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            i = 1
            for url in data_list:
                data_dict = create_info_book(url)
                print('\t--> ({}/{}){}'.format(i, pagination['nb_book'], data_dict['title']))
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
                if with_image:
                    extract_image(data_dict['image_url'])
                i += 1
    except IOError:
        print('I/O error')

if __name__ == '__main__':
    bts_url = 'http://books.toscrape.com'
    i= 1
    with_image = True
    category_url = extract_category_url(bts_url)
    if '-ni' in sys.argv:
        with_image = False
        del sys.argv[sys.argv.index('-ni')]

    if 'help' in sys.argv or '-h' in sys.argv:
        print('usage : main.py [\'-l\'] [\'-ni\'] [<category>]')
        print('\tcategory: extraction d\'une seule categorie')
        print('\t-l, --list: visualisation des categories')
        print('\t-ni: extraction sans image')
    elif '--list' in sys.argv or '-l' in sys.argv:
        print('\t--> Liste des catégories <--')
        for c in category_url:
            print('{}'.format(c['title']))
    else:
        if len(sys.argv) == 2:
            try:
                cat = next(item for item in category_url if item['title'].lower() == sys.argv[1].lower())
                category_url.clear()
                category_url = [cat]
            except:
                print('Catégorie inexistante')
        for cat in category_url:
            pagination = {'nb_category': len(category_url)}
            pagination['current_category'] = i
            category = extract_book_per_category(cat['url'])
            pagination['nb_book'] = len(category['books'])
            write_data_books_in_csv(category['books'], category['title'], pagination= pagination, with_image=with_image)
            i+=1
