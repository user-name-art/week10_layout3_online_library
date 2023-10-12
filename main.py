import os
import requests

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlsplit, unquote


url_template = 'https://tululu.org/txt.php?id='
folder = 'books'


def save_file(book, path):
    with open(path, 'wb') as file:
        file.write(book)


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def download_txt(url, folder):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """

    os.makedirs(folder, exist_ok=True)

    response = requests.get(url)
    response.raise_for_status()

    try:
        check_for_redirect(response)

        filename, author = get_book_author_and_name(number_of_book)

        filename_with_extension = f'{filename}.txt'
        path = os.path.join(folder, filename_with_extension)

        save_file(response.content, path)

        return path
    except requests.exceptions.HTTPError:
        print(f'По ссылке {url} нет книги для скачивания.')

    
def get_book_author_and_name(number_of_book):
    url_template = 'https://tululu.org/b'
    url = f'{url_template}{number_of_book}/'

    response = requests.get(url)
    response.raise_for_status()

    try:
        check_for_redirect(response)
    except requests.exceptions.HTTPError:
        return None, []

    soup = BeautifulSoup(response.text, 'lxml')
    book_name_and_author = soup.find('h1').text.split('::')
    name, author = book_name_and_author
    normal_name = sanitize_filename(name.strip())
    normal_author = sanitize_filename(author.strip())

    genres_html = soup.find('span', class_='d_book').find_all('a')
    all_genres = []
    for genre in genres_html:
        all_genres.append(genre.text)

    return normal_author, all_genres


def get_image_url(number_of_book):
    url_template = 'https://tululu.org/b'
    url = f'{url_template}{number_of_book}/'

    response = requests.get(url)
    response.raise_for_status()

    try:
        check_for_redirect(response)

        soup = BeautifulSoup(response.text, 'lxml')
        relative_image_url = soup.find('div', class_='bookimage').find('img')['src']
        image_url = urljoin('https://tululu.org', relative_image_url)

        return image_url
    except requests.exceptions.HTTPError:
        return None


def download_image(url, folder):
    os.makedirs(folder, exist_ok=True)

    response = requests.get(url)
    response.raise_for_status()

    try:
        check_for_redirect(response)

        path = urlsplit(url)

        filename = unquote(path.path).split('/')[-1]

        path = os.path.join(folder, filename)

        save_file(response.content, path)

        return filename
    except requests.exceptions.HTTPError:
        print(f'По ссылке {url} нет книги для скачивания.')


def get_book_comments(number_of_book):
    url_template = 'https://tululu.org/b'
    url = f'{url_template}{number_of_book}/'

    response = requests.get(url)
    response.raise_for_status()

    try:
        check_for_redirect(response)
    except requests.exceptions.HTTPError:
        return None

    soup = BeautifulSoup(response.text, 'lxml')
    text_html = soup.find('div', id='content').find_all('span', class_='black')

    all_comments = []
    for comment in text_html:
        all_comments.append(comment.text)

    return all_comments


if __name__ == '__main__':
    """    for number_of_book in range(1, 11):
        url = f'{url_template}{number_of_book}'
        print(download_txt(url, folder))"""
    for number_of_book in range(1, 11): 
        author, genres = get_book_author_and_name(number_of_book)
        print(author)
        [print(genre) for genre in genres]
        print(' ')
