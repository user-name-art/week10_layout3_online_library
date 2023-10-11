import os
import requests

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename

url_template = 'https://tululu.org/txt.php?id='
folder = 'books'


def save_image(book, path):
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

        save_image(response.content, path)

        return path
    except requests.exceptions.HTTPError:
        print(f'По ссылке {url} нет книги для скачивания.')

    
def get_book_author_and_name(number_of_book):
    url_template = 'https://tululu.org/b'
    url = f'{url_template}{number_of_book}'

    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')
    book_name_and_author = soup.find('h1').text.split('::')
    name, author = book_name_and_author
    normal_name = sanitize_filename(name.strip())
    normal_author = sanitize_filename(author.strip())

    return normal_name, normal_author


"""def get_book_from_site():
    os.makedirs(directory, exist_ok=True)

    number_of_book = 1
    url = f'{url_template}{number_of_book}'
    response = requests.get(url)
    response.raise_for_status()

    try:
        check_for_redirect(response)
        save_image(response.content, directory, filename_template, number_of_book)
    except requests.exceptions.HTTPError:
        print(f'По ссылке {url} нет книги для скачивания.')"""


if __name__ == '__main__':
    for number_of_book in range(1, 11):
        url = f'{url_template}{number_of_book}'
        print(download_txt(url, folder))
