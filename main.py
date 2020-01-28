#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import urllib.request
from bs4 import BeautifulSoup


def get_html(url):
    """

    :param url: str
    :return: bytes, html structure of the site
    """
    response = urllib.request.urlopen(url)
    return response.read()


def parse(html):
    """

    :param html: bytes, get html structure of the site
    :return: list of the candidates
    """
    soup = BeautifulSoup(html, features="html.parser")
    table = soup.find('table', class_='pure-table-bordered')

    candidates = []     # Contains all the candidates

    for row in table.find_all('tr')[1:]:    # From 1 so that to except header from the table
        cols = row.find_all('td')

        full_name = cols[0].a.text.split(' ')

        title_candidate = cols[1].b.text
        idx = title_candidate.find('№')

        if 'ОВО' in title_candidate:
            consignment = title_candidate[:idx-1]
        else:
            idx_comma = title_candidate.find(',')
            consignment = title_candidate[:idx_comma]

        number = title_candidate[idx + 1:]
        candidates.append({'surname': full_name[0], 'name': full_name[1], 'patronymic': full_name[2],
                           'consignment': consignment, 'number': number})

    return candidates


def get_page_count(html):
    """

    :param html: bytes, get html structure of the site
    :return: int, number of pages
    """
    soup = BeautifulSoup(html, features="html.parser")
    paggination = soup.find_all('table')[-1]

    return int(paggination.find_all('a')[-1].text[2:].split('-')[0]) // 30


def save(candidates, path):
    """

    :param candidates: list, list of all candidates
    :param path: str, path to file where saves all the candidates
    :return: Nothing
    """
    with open(path, 'w') as candidates_csv_file:
        writer = csv.writer(candidates_csv_file)
        writer.writerow(("Прізвище", "Ім'я", "По-батькові", "Партія", "Номер кандидата у списку"))

        for candidate in candidates:
            writer.writerow((candidate['surname'], candidate['name'], candidate['patronymic'], candidate['consignment'],
                             candidate['number']))


def main():
    ulr_site = 'https://www.cvk.gov.ua/pls/vnd2019/wp401pt001f01=919lit=192current_row=1.html'
    page_count = get_page_count(get_html(ulr_site))

    candidates = []

    for page in range(1, page_count + 2):
        candidates.extend(parse(get_html(ulr_site)))
        ulr_site = ulr_site.replace('current_row=' + str(1 + 30 * (page-1)), 'current_row=' + str(1 + 30*page))

    for candidate in candidates:
        print(candidate)

    save(candidates, 'candidates.csv')


if __name__ == "__main__":
    main()
