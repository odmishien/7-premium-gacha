from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import psycopg2
import os

genres = ['cold', 'process', 'frozen', 'confectionery', 'drink']
sub_genres = {}

def clawl(genres):
    base_url = 'https://www.sej.co.jp/i/products/7premium'
    genre_dict = {}
    for genre in genres:
        sub_genres = get_sub_genres(genre)
        sub_genre_dict = {}
        for sub_genre in sub_genres:
            page_url = urlopen('{base_url}/{genre}/{sub_genre}/?page=1&limit=100'.format(base_url=base_url, genre=genre, sub_genre=sub_genre))
            products_info_list = get_products_info(page_url)
            sub_genre_dict[sub_genre] = products_info_list
        genre_dict[genre] = sub_genre_dict
    return genre_dict

def get_sub_genres(genre):
    url = urlopen('https://www.sej.co.jp/i/products/7premium/' + genre)
    soup = BeautifulSoup(url, 'html.parser')
    sub_genre_sections = soup.find_all('div', 'subCategory')
    sub_genres = []
    for sub_genre_section in sub_genre_sections:
        line_up_section = sub_genre_section.find('div', 'lineup')
        sub_genre_link = line_up_section.find('a').get('href')
        sub_genre = re.sub('(/i/products/7premium/%s/)' %genre,'',sub_genre_link)
        sub_genre = re.sub('(\/\?page=1)', '', sub_genre)
        sub_genres.append(sub_genre)
    return sub_genres

def get_products_info(url):
    products_info = []
    soup = BeautifulSoup(url, 'html.parser')
    products_section = soup.find('ul', 'itemList')
    products = products_section.find_all('li', 'item')
    for product in products:
        try:
            name = product.find('div', 'itemName').string
            prices = product.find('li', 'price').string
            pattern = r'(\d+)(円)(（税込)(\d+)(円）)'
            regex = re.compile(pattern)
            result = regex.search(prices)
            price = result.group(1)
            price_with_tax = result.group(4)
            products_info.append((name, price, price_with_tax))
        except:
            print(product)
    return products_info

def get_connection():
    dsn = os.environ.get('DATABASE_URL') or "postgresql://localhost/seven_premium_gacha"
    return psycopg2.connect(dsn)

def update_table(product_list):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('DROP TABLE IF EXISTS seven_premium_products;')
            cur.execute('CREATE TABLE seven_premium_products (id SERIAL PRIMARY KEY, product_name varchar(40) NOT NULL, genre varchar(40) NOT NULL, sub_genre varchar(40) NOT NULL, price smallint NOT NULL, price_with_tax smallint NOT NULL);')

    for genre in product_list.keys():
        for sub_genre in product_list[genre].keys():
            for product_info in product_list[genre][sub_genre]:
                name = product_info[0]
                price = product_info[1]
                price_with_tax = product_info[2]
                with get_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute("INSERT INTO seven_premium_products (product_name, genre, sub_genre, price, price_with_tax) VALUES (%s, %s, %s, %s, %s);", (name, genre, sub_genre, price, price_with_tax,))
                    conn.commit()

product_list = clawl(genres)
update_table(product_list)
