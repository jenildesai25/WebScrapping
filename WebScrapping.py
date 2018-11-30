from bs4 import BeautifulSoup
import requests

if __name__ == '__main__':
    user_input = input('What is the year that you are interested in getting data:')
    url = 'https://www.boxofficemojo.com/yearly/chart/?yr=' + user_input + '&p=.htm%20'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # print('page data is:', soup)
    # the data we needed is after <b> so we can find it by find_all function
    scrapped_data = []
    # data comes in unicode you need to convert to string.encode will help you in that.
    for movie_name_and_total_gross in soup.find_all('b'):
        # data comes in unicode you need to convert to string.encode will help you in that.
        scrapped_data.append(movie_name_and_total_gross.text)
    print(scrapped_data)
    ids_of_movie = []
    for ids in soup.find_all('a', href=lambda href: href and "movies" in href):
        # print(ids['href'])
        ids_of_movie.append(ids['href'])
    print(ids_of_movie)
