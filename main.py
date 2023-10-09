import os
import requests


filename_template = 'id'
directory = 'books'
url_template = 'https://tululu.org/txt.php?id='


def save_image(book, directory, filename_template, number_of_book):
    with open(f'{directory}/{filename_template}{number_of_book}.txt', 'wb') as file:
        file.write(book)


def get_book_from_site():
    os.makedirs(directory, exist_ok=True)

    for number_of_book in range(1, 11):
        url = f'{url_template}{number_of_book}'
        response = requests.get(url)
        response.raise_for_status() 

        save_image(response.content, directory, filename_template, number_of_book)

if __name__ == '__main__':
    get_book_from_site()
