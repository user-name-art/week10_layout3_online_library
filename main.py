import os
import sys
import requests
import argparse

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlsplit, unquote


def save_file(book, path):
    with open(path, 'wb') as file:
        file.write(book)


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def parse_book_page(soup):
    book_name_and_author = soup.find('h1').text.split('::')
    name, author = book_name_and_author
    normal_name = sanitize_filename(name.strip())
    normal_author = sanitize_filename(author.strip())

    genres_html = soup.find('span', class_='d_book').find_all('a')
    genres = [genre.text for genre in genres_html]

    relative_image_url = soup.find('div', class_='bookimage').find('img')['src']
    image_url = urljoin('https://tululu.org', relative_image_url)

    comment_html = soup.find('div', id='content').find_all('span', class_='black')

    comments = [comment.text for comment in comment_html]

    book_info = {
        'name': normal_name,
        'author': normal_author,
        'genres': genres,
        'image_url': image_url,
        'comments': comments,
    }

    return book_info


def download_txt(url, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    os.makedirs(folder, exist_ok=True)

    response = requests.get(url)
    response.raise_for_status()

    try:
        check_for_redirect(response)

        filename_with_extension = f'{filename}.txt'
        path = os.path.join(folder, filename_with_extension)

        save_file(response.content, path)

        return path
    except requests.exceptions.HTTPError:
        print(f'Книга {filename} недоступна для скачивания.')


def download_image(url, folder='images/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на картинку, который хочется скачать.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранёна картинка.
    """
    os.makedirs(folder, exist_ok=True)

    response = requests.get(url)
    response.raise_for_status()

    try:
        check_for_redirect(response)

        link = urlsplit(url)

        filename = unquote(link.path).split('/')[-1]

        path = os.path.join(folder, filename)

        save_file(response.content, path)

        return path
    except requests.exceptions.HTTPError:
        print(f'По ссылке {url} нет картинки для скачивания.')


def main():
    parser = argparse.ArgumentParser(description='Скрипт скачивает книги с сайта tululu.org.')
    parser.add_argument('start_id', nargs='?', default=1, type=int, help='id первой книги для скачивания.')
    parser.add_argument('end_id', nargs='?', default=1, type=int, help='id последней книги для скачивания.')
    first_book_id = parser.parse_args().start_id
    last_book_id = parser.parse_args().end_id + 1

    for book_number in range(first_book_id, last_book_id):
        url_template = 'https://tululu.org/b'
        url = f'{url_template}{book_number}/'
        
        response = requests.get(url)
        response.raise_for_status()

        try:
            check_for_redirect(response)
            soup = BeautifulSoup(response.text, 'lxml')
            book_info = parse_book_page(soup)
        except requests.exceptions.HTTPError:
            book_info = {}
        
        if book_info:
            print(book_info['name'])
            print(book_info['author'])
            print('')

            book_download_url = f'https://tululu.org/txt.php?id={book_number}/'
            filename = book_info['name']
            path = download_txt(book_download_url, filename)

            if path:
                image_url = book_info['image_url']
                download_image(image_url)


if __name__ == '__main__':
    main()
