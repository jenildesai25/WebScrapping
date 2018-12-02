
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import glob
import re

file_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
file_path = os.path.join(file_path, 'BoxOfficeMojo2_virti_bipin')
if not os.path.exists(str(file_path)):
    os.mkdir(str(file_path))
os.chdir(file_path)

if len(glob.glob("*")) != 0:
    file_list = glob.glob("*")
    for file in file_list:
        os.remove(file)

url = 'https://www.boxofficemojo.com/people/?view=Actor&pagenum=1&sort=sumgross&order=DESC&&p=.htm'.format(
        1)
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
        url = 'https://www.boxofficemojo.com/people/?view=Actor&pagenum=1&sort=sumgross&order=DESC&&p=.htm'.format(
            num)  # This one works
        print("Grabbing page for {}".format(num))
        r = requests.get(url)
        html = r.text
        soup = BeautifulSoup(html, 'lxml')
        table = soup.find('table', {"cellspacing": "1"})
        df = pd.read_html(str(table), skiprows=2)
        df = df[0]
        df = df.iloc[:, :7]
        df.columns = ['rank', 'name', 'id', 'total gross', 'number of movies', 'Number 1 Picture']
        df = df[:len(df.index) - 3]
        df = df[['rank', 'name', 'id', 'total gross', 'number of movies', 'Number 1 Picture']]

        df['id'] = ''

        id_list = []
        title_list = df['rank'].tolist()

        for link in soup.findAll('a', {'href': re.compile("\?id=")}):
            id_list.append(link.get('href'))

        id_list = [x.split('=')[1] for x in id_list]
        id_list = [x.split('.')[0] for x in id_list]
        id_list = id_list[1:]
        id_dict = dict(zip(title_list, id_list))

        print(df)

        for index in df.index:
            df.loc[index, 'id'] = id_dict[df.loc[index, 'title']]

        # df.to_csv("{}-{}.csv".format(year, num), index=False)
        df.to_csv("{}-{}.csv".format(num), index=False)

    except Exception as e:
        print(e)

    file_list = glob.glob("*.csv")
    df_container = []

    for file in file_list:
        df = pd.read_csv(file)
        df_container.append(df)

    df_combined = pd.concat(df_container)
    df_combined.to_csv("actors.txt", index=False, sep="\t")

    files_to_delete_list = glob.glob("*.csv")

    for file in file_list:
        os.remove(file)

    df = pd.read_csv("actors.txt", sep="\t")

    df['total gross'] = df['total gross'].apply(lambda x: x.replace('$', ''))
    df['total gross'] = df['total gross'].apply(lambda x: x.replace(',', ''))
    df['total gross'] = df['total gross'].apply(lambda x: int(x))

    highest_gross_earnings = '${:,.2f}'.format(df['total gross'].max())

    df = df.sort_values(by='total theaters', ascending=False)

    most_movies = df.iloc[0]['name']
    most_movies_total = int(df.iloc[0]['number of movies'])

    print("---------------------------")
    print("The highest total gross earnings was {}".format(highest_gross_earnings))
    print("The actor with the maximum number of movies was '{}' with {}".format(most_movies, most_movies_total))