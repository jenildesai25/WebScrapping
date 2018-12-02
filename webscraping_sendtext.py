# import bs4 as bs
# import urllib.request
# user_input = input('What is the year that you are interested in getting data:')
# url = 'https://www.boxofficemojo.com/yearly/chart/?page=1&view=releasedate&view2=domestic&yr=' + user_input + '&p=.htm'
# sauce = urllib.request.urlopen(url).read()
#
# #turn into beautiful soup object
# soup = bs.BeautifulSoup(sauce, 'lxml')
#
# print(soup.find_all('href'))



# NEW CODE #

# This is the final version

# https://old.reddit.com/r/learnpython/comments/a02wyv/please_help_python_web_scraping_project/

"""
For some reason, my year 2018 average total doesn't match up with that BoxOfficeMojo has on the "Averages" section
at the bottom of the page. All other years match. Not sure why that is, but I'm confident my data / scraping is accurate.

MAKE SURE TO SPECIFY THE FILE PATH if you want a different one than what I have below and make sure it doesn't contain
any files. Or else this script will erase all of your files in that directory. You can add in an input statement to ask
the user for a directory.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import glob
import re

print(
    "Welcome to Internet Movie Scraper Database (IMSDB). Please specify a year, and we will create a text document that"
    "will tell you all about the movie business that year.")

file_path = "C:/Users/Virti Sanghavi/Pictures/boxofficemojo"  # Where you want to write the file to. Make sure to specify the location, as stated above.

if os.path.exists(str(file_path)) is False:
    os.mkdir(str(file_path))

os.chdir(file_path)

if len(glob.glob("*")) != 0:
    file_list = glob.glob("*")
    for file in file_list:
        os.remove(file)

year = input(
    "Please enter a year as a valid integer between the year 2018 and 1980: ")  # Need to add in try/except blocks here.

try:
    year = int(year)

except:
    print("You must enter in a valid integer. Closing down...")
    exit()

if not 1980 <= year <= 2018:
    print("You must enter in a an integer between 1980 and 2018. Closing down...")
    exit()

# pulling a range is a little sloppy. I could find the total number of pages and use that as the range--there were never
# more than 1000 movies released any year (or at least that Box Office Mojo tracks. One could find the actual number of
# pages scraped. But I didn't do that. Maybe you can.
url = 'https://www.boxofficemojo.com/yearly/chart/?page={}&view=releasedate&view2=domestic&yr={}&p=.htm'.format(
    1, year)
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
for num in range(1, len(total_pages) + 1, 1):
    try:
        url = 'https://www.boxofficemojo.com/yearly/chart/?page={}&view=releasedate&view2=domestic&yr={}&p=.htm'.format(
            num, year)  # This one works
        print("Grabbing page {} for {}".format(num, year))
        r = requests.get(url)
        html = r.text
        soup = BeautifulSoup(html, 'lxml')
        table = soup.find('table', {"cellspacing": "1"})
        df = pd.read_html(str(table), skiprows=2)
        df = df[0]
        df = df.iloc[:, :7]  # This slices the dataframe to cut off the date sections.
        df.columns = ['rank', 'title', 'studio', 'total gross', 'total theaters', 'opening gross', 'opening theaters']
        df = df[:len(df.index) - 3]
        df = df[['title', 'studio', 'total gross', 'total theaters', 'opening gross', 'opening theaters']]

        df['id'] = ''

        # This is to get the IDs. Usually iterating through a DataFrame is a no-no, because it's very inefficient. But
        # I wanted to get this done quickly.

        id_list = []
        title_list = df['title'].tolist()

        for link in soup.findAll('a', {'href': re.compile("\?id=")}):  # Getting the ids
            id_list.append(link.get('href'))  # add to id list

        id_list = [x.split("=")[1] for x in id_list]  # isolating the id 1
        id_list = [x.split(".")[0] for x in id_list]  # isolating the id 2
        id_list = id_list[
                  1:]  # cutting off the first entry (first entry gives the #1 box office entry for the current week).
        id_dict = dict(zip(title_list, id_list))

        for index in df.index:
            df.loc[index, 'id'] = id_dict[df.loc[index, 'title']]

        df.to_csv("{}-{}.csv".format(year, num), index=False)

    except ValueError:
        continue

file_list = glob.glob("*.csv")
df_container = []

for file in file_list:
    df = pd.read_csv(file)
    df_container.append(df)

df_combined = pd.concat(df_container)
df_combined.to_csv("movies.txt", index=False, sep="\t")

files_to_delete_list = glob.glob("*.csv")

for file in file_list:
    os.remove(file)

df = pd.read_csv("movies.txt", sep="\t")

# Clean the data, else it won't be able to get the mean of the total gross.
df['total gross'] = df['total gross'].apply(lambda x: x.replace('$', ''))  # replace dollar signs
df['total gross'] = df['total gross'].apply(lambda x: x.replace(',', ''))  # replace commas
df['total gross'] = df['total gross'].apply(lambda x: int(x))  # turn it from a str to int

# Dollar formatting. :) See here: https://stackoverflow.com/questions/21208376/converting-float-to-dollars-and-cents
average_gross_earnings = '${:,.2f}'.format(df['total gross'].mean())

df = df.sort_values(by='total theaters', ascending=False)  # sorts the DataFrame to get the highest theater number.

movie_most_theaters = df.iloc[0]['title']
most_theaters_total = int(df.iloc[0]['total theaters'])

print("---------------------------")
print("The average total gross earnings for the year {} was {}".format(year, average_gross_earnings))
print("The movie that was shown in the most theaters was '{}' with {} theaters".format(movie_most_theaters,
                                                                                       most_theaters_total))
