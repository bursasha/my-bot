import requests
from bs4 import BeautifulSoup
import re


def kenex_parser():
    kenex_results = []
    i = 1
    while i <= 5:
        url = 'https://www.kenex.cz/televizory:finlux/strana-{number}'+'/'
        url = url.format(number=i)
        req = requests.get(url)
        html = req.content
        soup = BeautifulSoup(html, 'lxml')
        tvs = soup.find_all('li', class_='product')

        for x in tvs:
            name = x.find('div', class_='p-info').find('span').get_text(strip=True).lower()
            availability = x.find('span', class_='p-cat-availability').get_text(strip=True).lower()
            if 'obj' in availability:
                availability = 'Не на складе'
            else:
                availability = 'На складе'
            href = x.find('div', class_='p-info').find('a').get('href').lower()
            kenex_results.append({'name': name, 'availability': availability, 'href': href})

        i += 1
    return kenex_results


def mascom_parser():
    mascom_results = []
    i = 1
    while i <= 6:
        if i == 1:
            url = 'https://www.satshop.cz/TV/'
        elif i > 1:
            url = 'https://www.satshop.cz/TV/{number}'+'/'
            url = url.format(number=i)
        req = requests.get(url)
        html = req.content
        soup = BeautifulSoup(html, 'lxml')
        tvs = soup.find_all('div', class_='product')

        for x in tvs:
            name = x.find('strong', class_='h3').find('a').get('title').lower()
            availability = x.find('strong', class_='h3').find('div').get_text().lower().split()
            availability = ' '.join(availability)
            if 'není' in availability:
                availability = 'Не на складе'
            else:
                availability = 'На складе'
            href = x.find('a', class_='picture').get('href').lower()
            mascom_results.append({'name': name, 'availability': availability, 'href': href})

        i += 1
    for i in mascom_results:
        i['name'] = re.sub(r'^\w* tv', i['name'].split(' ')[0]+' ' , i['name'])
    return mascom_results


def tv():
    kenex_parser_results = kenex_parser()
    mascom_parser_results = mascom_parser()
    results = []
    for x in kenex_parser_results:
        for i in mascom_parser_results:
            if x['name'][0:18] in i['name'] and x['availability']!=i['availability']:
                results.append({'name': x['name'], 'first_availability': x['availability'],\
                'second_availability': i['availability'],\
                'first_href': 'https://www.kenex.cz' + x['href'], 'second_href': i['href']})

    if not results:
        text = '📺<b>Телевизоры:</b>\n\n'+'Доступность телевизоров на Kenex соответствует доступности на Mascom✅'
        return text

    else:
        results.sort(key = lambda n: n['name'])
        text = '📺<b>Список телевизоров:</b>\n\n'
        for r in results:
            text += f'<b>Модель:</b> {r["name"]}\n' +\
            f'<b>Доступность на Kenex:</b> {r["first_availability"]}\n' +\
            f'<b>Доступность на Mascom:</b> {r["second_availability"]}\n' +\
            f'<b>Ссылка Kenex:</b> {r["first_href"]}\n' +\
            f'<b>Ссылка Mascom:</b> {r["second_href"]}\n\n'
        return text
