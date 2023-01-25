import requests
from bs4 import BeautifulSoup
import lxml
import csv

url = 'https://www.dotabuff.com/heroes'

headers = {'Accept': '*/*',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.124 YaBrowser/22.9.2.1495 Yowser/2.5 Safari/537.36'}


def get_data(url, headers):
    req = requests.get(url, headers=headers)
    src = req.text
    with open('index.html', 'w', encoding='utf-8') as file:
        file.write(src)
    return src


def parse_heroes_urls(src):
    soup = BeautifulSoup(src, 'lxml')
    all_heroes = soup.find(class_='hero-grid').find_all('a')
    all_heroes_dict = {}
    for item in all_heroes:
        item_text = item.text
        item_href = 'https://www.dotabuff.com' + item.get('href')
        all_heroes_dict[item_text] = item_href
    return all_heroes_dict


def find_mui(all_sections):
    for i in range(len(all_sections)):
        if all_sections[i].find('header') is not None:
            if all_sections[i].find('header').text == 'Most Used ItemsThis Week more':
                return i


def parse_hero_info(hero_name, hero_url):
    hero_name = hero_name.strip()
    req = requests.get(url=hero_url, headers=headers)
    src = req.text
    with open(f'html/{hero_name}.html', 'w', encoding='utf-8') as file:
        file.write(src)
    soup = BeautifulSoup(src, 'lxml')
    info = soup.find(class_='col-8').find('section')

    all_sections = soup.find(class_='col-8').find_all('section')

    most_used_items = all_sections[find_mui(all_sections)]
    header_mui = most_used_items.find('header').text
    header_mui = header_mui.split()[:3]
    header_mui[2] = header_mui[2].split('T')[0]
    header_mui = (''.join(header_mui)).split()

    head = most_used_items.find('article').find('table').find('thead').find('tr').find_all('th')
    body = most_used_items.find('article').find('table').find('tbody').find_all('tr')

    head_list = []
    for i in head:
        head_list.append(i.text)

    items_info = []
    for i in body:
        items_info.append(i.find_all('td'))

    for i in range(len(items_info)):
        for j in range(len(items_info[i])):
            items_info[i][j] = items_info[i][j].text
    for i in range(len(items_info)):
        items_info[i] = items_info[i][1:]
    return head_list, items_info, header_mui

def parse_lanes_info(source):
    soup = BeautifulSoup(source, 'lxml')
    info = soup.find(class_='col-8').find('section')
    header = info.find('article').find('table').find('thead').find('tr').find_all('th')
    table = info.find('article').find('table').find('tbody').find_all('tr')

    header_list = []
    for i in header:
        header_list.append(i.text)

    lanes_info = []
    for i in table:
        lanes_info.append(i.find_all('td'))

    for i in range(len(lanes_info)):
        for j in range((len(lanes_info[i]))):
            lanes_info[i][j] = lanes_info[i][j].text
            if '.' in lanes_info[i][j]:
                lanes_info[i][j] = lanes_info[i][j].replace('.', ',')
    return header_list, lanes_info

def main():
    src = get_data(url=url, headers=headers)
    all_heroes_dict = parse_heroes_urls(src)
    for hero_name, hero_url in all_heroes_dict.items():
        hero_name = hero_name.strip()
        head_list, items_info, header_mui = parse_hero_info(hero_name, hero_url)
        with open(f'csv/{hero_name}.csv', 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file, delimiter=';', )
            writer.writerow(header_mui)

        with open(f'csv/{hero_name}.csv', 'a', encoding='utf-8', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(head_list)

        for j in range(len(items_info)):
            with open(f'csv/{hero_name}.csv', 'a', encoding='utf-8', newline='') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(items_info[j])

        with open(f'html/{hero_name}.html', 'r', encoding='utf-8') as file:
            src = file.read()
            header_list, lanes_info = parse_lanes_info(src)
            file.close()

        with open(f'csv/{hero_name}.csv', 'a', encoding='utf-8', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerows(('', header_list))

        for j in range(len(lanes_info)):
            with open(f'csv/{hero_name}.csv', 'a', encoding='utf-8', newline='') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(lanes_info[j])


if __name__ == "__main__":
    main()
