from bs4 import BeautifulSoup
import urllib2

if __name__ == '__main__':
    user_input = raw_input('What is the year that you are interested in getting data:')
    page = 'https://www.boxofficemojo.com/yearly/chart/?yr=' + user_input + '&p=.htm%20'
    page_open = urllib2.urlopen(page)
    soup = BeautifulSoup(page_open, 'html.parser')
    # print(soup)
    # the data we needed is after <b> so we can find it by find_all function
    scrapped_data = []
    # data comes in unicode you need to convert to string.encode will help you in that.
    for movie_name_and_total_gross in soup.find_all('b'):
        # data comes in unicode you need to convert to string.encode will help you in that.
        scrapped_data.append(movie_name_and_total_gross.text.encode('UTF8'))
    # print(scrapped_data)
    ids_of_movie = []
    for ids in soup.find_all('a'):
        ids_of_movie.append(ids.text.encode('UTF8'))
    print(ids_of_movie)
