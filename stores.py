from abc import ABCMeta, abstractmethod

import re
import requests
from bs4 import BeautifulSoup


class AbstractShop(metaclass=ABCMeta):
    url = ''
    shop_name = ''
    source_constructor = ''
    comics = []

    def _check_page(self, number_of_page):
        page_url = f'{self.url}{number_of_page}/'
        request = requests.get(page_url)
        src = request.text
        soup = BeautifulSoup(src, 'lxml')
        if self._empty_page_check(soup):
            return None
        else:
            return soup

    @abstractmethod
    def _empty_page_check(self, soup):
        pass

    @abstractmethod
    def _add_page_in_comics_list(self, soup):
        pass

    @staticmethod
    def _check_comic(search_term, comic):
        terms = re.split(' |,|-|_', search_term)
        if comic.get('in_shop') and all([term.strip().lower() in comic.get('name').lower() for term in terms]):
            return True
        else:
            return False

    def update_comics_list(self):
        self.comics = []
        number_of_page = 1
        while True:
            print(f'{self.shop_name}, page #{number_of_page}')
            soup = self._check_page(number_of_page)
            if not soup:
                break
            self._add_page_in_comics_list(soup)
            number_of_page += 1

    def comics_filter(self, search_term):
        return [comic for comic in self.comics if self._check_comic(search_term, comic)]


class OnTheBus(AbstractShop):
    url = 'https://www.onthebus.com.ua/komiksy/?page='
    shop_name = 'On the Bus'
    source_constructor = 'https://www.onthebus.com.ua'
    comics = []

    def _add_page_in_comics_list(self, soup):
        all_result = soup.find_all(class_="image")
        for comic in all_result:
            name = comic.find('a').get('title')
            source = f'{self.source_constructor}{comic.find("a").get("href")}'
            in_shop = 'Купить' in str(comic)
            self.comics.append({'name': name, 'source': source, 'in_shop': in_shop})

    def _empty_page_check(self, soup):
        return soup.find('p', class_='align-center double-padded')


class Cosmic(AbstractShop):
    url = 'https://cosmic.com.ua/comics/filter/page='
    shop_name = 'Cosmic'
    source_constructor = 'https://cosmic.com.ua'
    comics = []

    def _add_page_in_comics_list(self, soup):
        all_result = soup.find_all('div', class_="catalogCard-view")
        for comic in all_result:
            name = comic.find('img').get('alt')
            source = f'{self.source_constructor}{comic.find("a").get("href")}'
            in_shop = not bool(comic.find('a', class_="catalogCard-image __grayscale"))
            self.comics.append({'name': name, 'source': source, 'in_shop': in_shop})

    def _empty_page_check(self, soup):
        return soup.find('body', class_='error-page')


class Geekach(AbstractShop):
    url = 'https://geekach.com.ua/komiksy/filter/page='
    shop_name = 'Geekach'
    source_constructor = 'https://geekach.com.ua'
    comics = []

    def _add_page_in_comics_list(self, soup):
        all_result = soup.find_all('div', class_='catalogCard-info')
        for comic in all_result:
            name = comic.find('div', class_='catalogCard-title').find('a').get('title')
            source = f'{self.source_constructor}{comic.find("a").get("href")}'
            in_shop = bool('В наличии' in comic.find('div', class_='catalogCard-availability').text)
            self.comics.append({'name': name, 'source': source, 'in_shop': in_shop})

    def _empty_page_check(self, soup):
        return soup.find('div', class_='error-page-container')


class Bookovka(AbstractShop):
    url = 'https://www.bookovka.ua/ru/2207-komiksy?p='
    shop_name = 'Bookovka'
    old_page = None
    comics = []

    def _add_page_in_comics_list(self, soup):
        all_result = soup.find_all('div', class_='right-block')
        for comic in all_result:
            name = comic.find('a').get('title')
            source = comic.find('a').get('href')
            in_shop = bool('В наличии' in comic.find('span', class_='stock_label').text)
            self.comics.append({'name': name, 'source': source, 'in_shop': in_shop})

    def _empty_page_check(self, soup):
        all_result = soup.find_all('div', class_='right-block')
        answer = all_result == self.old_page
        self.old_page = all_result
        return answer
