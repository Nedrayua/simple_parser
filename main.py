
import asyncio
import aiohttp
import csv
import json
import os
from bs4 import BeautifulSoup
from datetime import datetime


JSON_FILENAME =  'knigocom_{}.json'
CSV_FILENAME = 'knigocom_{}.csv'
DIR_COLLECT_DATA = 'data'
MAINDIR = os.path.dirname(os.path.abspath(__file__))


if not os.path.exists(os.path.join(MAINDIR, DIR_COLLECT_DATA)):
    os.mkdir(os.path.join(MAINDIR, DIR_COLLECT_DATA))

start_time = datetime.now()
books_data = []

row_names = {
            'book_name':'Book title',
            'book_author': 'Author of the book',
            'book_link': 'Link to the book'}
row_name = ['book_name', 'book_author', 'book_link']


async def get_page_data(session, page):
    """
    Runs on resources and collect data
    """

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Mobile Safari/537.36'
    }

    url = f'https://knigogo.com.ua/bezkoshtovni-knigi/page/{page}/'

    async with session.get(url=url, headers=headers) as response:
        response_text = await response.text()

        soup = BeautifulSoup(response_text, 'lxml')

        book_items = soup.find('div', class_='book_container animation').find_all('div', class_="book_desk2")
        
        for book in book_items:
            
            try:
                book_name = book.find('a').text
            except AttributeError:
                book_name = 'Noname'
            try:
                book_author = book.find('span', class_='book_autor').find('a').text
            except AttributeError:
                book_author = 'No author'
            try:
                book_link = book.find('a').get('href')
            except AttributeError:
                book_link = 'No link'
        
            books_data.append(
                    {
                        'book_name': book_name,
                        'book_author': book_author,
                        'book_link': book_link
                    }
                )
        print(f'[INFO] Processed page: {page}')

async def gather_data():
    """
    Contains a useful list of tasks
    """
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Mobile Safari/537.36'
    }

    url = "https://knigogo.com.ua/bezkoshtovni-knigi/"

    async with aiohttp.ClientSession() as session:

        response = await session.get(url=url, headers=headers)
        soup = BeautifulSoup(await response.text(), 'lxml')
        page_count = soup.find("ul", class_="filter_list").find_all("a")[-2].text

        tasks = []

        for page in range(1, int(page_count) + 1):
            task = asyncio.create_task(get_page_data(session, page))
            tasks.append(task)
        
        await asyncio.gather(*tasks)


def main():
    asyncio.run(gather_data())
    current_time = datetime.now().strftime('%d-%m-%Y')
    jsonfile = os.path.join(DIR_COLLECT_DATA, JSON_FILENAME.format(current_time))
    csvfile = os.path.join(DIR_COLLECT_DATA, CSV_FILENAME.format(current_time))

    with open(jsonfile, 'w') as file:
        json.dump(books_data, file, indent=4, ensure_ascii=False)


    with open(csvfile, 'a') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=row_name)
        writer.writerow(row_names)
        writer.writerows(books_data)
        
    finish_time = datetime.now()- start_time
    print(f'[INFO] Script take {finish_time}')


if __name__ == '__main__':
    main()

