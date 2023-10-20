import os
import sys
import requests
import argparse
import time

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlsplit, unquote


URL_TEMPLATE = 'https://tululu.org/b'


def save_file(book, path):
    with open(path, 'wb') as file:
        file.write(book)


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def parse_book_page(soup, url):
    book_name_and_author = soup.find('h1').text.split('::')
    name, author = book_name_and_author
    normal_name = sanitize_filename(name.strip())
    normal_author = sanitize_filename(author.strip())

    genres_html = soup.find('span', class_='d_book').find_all('a')
    genres = [genre.text for genre in genres_html]

    relative_image_url = soup.find('div', class_='bookimage').find('img')['src']
    
    image_url = urljoin(url, relative_image_url)

    comment_html = soup.find('div', id='content').find_all('span', class_='black')

    comments = [comment.text for comment in comment_html]

    book = {
        'name': normal_name,
        'author': normal_author,
        'genres': genres,
        'image_url': image_url,
        'comments': comments,
    }

    return book


def download_txt(content, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        content (bytes): Cодержание ответа сервера в байтах.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    os.makedirs(folder, exist_ok=True)

    filename_with_extension = f'{filename}.txt'
    path = os.path.join(folder, filename_with_extension)

    save_file(content, path)

    return path


def download_image(content, url, folder='images/'):
    """Функция для скачивания картинок.
    Args:
        content (bytes): Cодержание ответа сервера в байтах.
        url (str): Cсылка на картинку, которую хочется скачать.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранёна картинка.
    """
    os.makedirs(folder, exist_ok=True)

    link = urlsplit(url)

    filename = unquote(link.path).split('/')[-1]

    path = os.path.join(folder, filename)

    save_file(content, path)

    return path


def main():
    parser = argparse.ArgumentParser(description='Скрипт скачивает книги с сайта tululu.org.')
    parser.add_argument('start_id', nargs='?', default=1, type=int, help='id первой книги для скачивания.')
    parser.add_argument('end_id', nargs='?', default=100, type=int, help='id последней книги для скачивания.')
    first_book_id = parser.parse_args().start_id
    last_book_id = parser.parse_args().end_id + 1

    for book_number in range(first_book_id, last_book_id):
        while True:
            try:
                url = f'{URL_TEMPLATE}{book_number}/'

                response = requests.get(url)
                response.raise_for_status()
                check_for_redirect(response)
                soup = BeautifulSoup(response.text, 'lxml')
                book = parse_book_page(soup, url)

                filename = book['name']
                book_download_url = 'https://tululu.org/txt.php'
                payload = {'id': book_number}
                response = requests.get(book_download_url, params=payload)
                response.raise_for_status()
                check_for_redirect(response)
                download_txt(response.content, filename)

                image_url = book['image_url']
                response = requests.get(image_url)
                response.raise_for_status()         
                download_image(response.content, image_url)

                print(book['name'])
                print(book['author'])  
                print('')

                break
            except requests.exceptions.ConnectionError:
                print('Нет подключения к сайту, ждем.\n')
                time.sleep(2)
            except requests.exceptions.HTTPError:
                print(f'По ссылке {url} нет книги.\n')
                break


if __name__ == '__main__':
    main()    
