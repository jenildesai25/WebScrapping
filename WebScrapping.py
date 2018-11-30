from bs4 import BeautifulSoup
import requests


class WebScrapping:

    def __init__(self, url, user_input):
        self.url = url
        self.user_input = user_input
        self._load_data_from_url()

    def _load_data_from_url(self):
        scrapped_data = []
        ids_of_movie = []
        pages_data = []
        total_pages = []
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        for page in soup.find_all('a', href=lambda href: href and "page" in href):
            pages_data.append(page['href'])
        for page in pages_data:
            if 'page' in page:
                index = page.find('page')
                if page[index:index + 6] not in total_pages:
                    total_pages.append(page[index:index + 6])
        for i in range(1, len(total_pages) + 1):
            new_url = 'https://www.boxofficemojo.com/yearly/chart/?page{}&view=releasedate&view2=domestic&yr={}&p=.htm'.format(i, self.user_input)
            response = requests.get(new_url)
            data = BeautifulSoup(response.content, 'html.parser')
            # the data we needed is after <b> so we can find it by find_all function
            # data comes in string.
            for movie_name_and_total_gross in data.find_all('b'):
                scrapped_data.append(movie_name_and_total_gross.text)
            print('\n'.join(scrapped_data))
            for ids in data.find_all('a', href=lambda href: href and "movies" in href):
                ids_of_movie.append(ids['href'])
            print('\n'.join(ids_of_movie))


if __name__ == '__main__':
    user_input = input('What is the year that you are interested in getting data:')
    url = 'https://www.boxofficemojo.com/yearly/chart/?page=1&view=releasedate&view2=domestic&yr=' + user_input + '&p=.htm'
    web_scrapping_object = WebScrapping(url=url, user_input=user_input)
