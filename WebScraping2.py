
# Online References used :
# https://github.com/imadmali/movie-scraper/blob/master/MojoLinkExtract.py
# https://www.crummy.com/software/BeautifulSoup/bs4/doc/
# https://nycdatascience.com/blog/student-works/scraping-box-office-mojo/
# https://www.youtube.com/watch?v=XQgXKtPSzUI
# https://www.youtube.com/watch?v=aIPqt-OdmS0
# https://www.youtube.com/watch?v=XQgXKtPSzUI
from bs4 import BeautifulSoup
import pandas as pd
import os
import requests
import glob
import re



def scrape_data_for_actors():
        file_path = os.path.join(os.path.join(os.environ['USERPROFILE']),
                                 'Desktop')  # This is written in order to save the txt file in the user's specified location on the machine
        file_path = os.path.join(file_path,
                                 'BoxOfficeMojo2_virti_bipin')  # Folder name to be created where the file will be stored
        if not os.path.exists(str(file_path)):
            os.mkdir(str(file_path))  # If path does not exist create the path
        os.chdir(file_path)  # Change the directory of the file path

        if len(glob.glob(
                "*")) != 0:  # The glob module finds all the pathnames matching a specified pattern according to the rules used by the Unix shell
            file_list = glob.glob("*")
            for file in file_list:
                os.remove(file)

        # The url of the BoxOffice Mojo to be scraped
        url = 'https://www.boxofficemojo.com/people/?view=Actor&pagenum=1&sort=sumgross&order=DESC&&p=.htm'
        pages_data = []  # List to store the pages data
        total_pages = []
        response = requests.get(url)  # Get the response of the url after passing the user input
        soup = BeautifulSoup(response.content,
                             'html.parser')  # Using the beautiful soup library to parse the html content and format it
        for page in soup.find_all('a', href=lambda href: href and "page" in href):  # find the href in a tags
            pages_data.append(page['href'])  # append the data in the pages_data list
        for page in pages_data:
            if 'page' in page:  # If "page" found in href
                index = page.find('page')  # Take the index of that page if found

                # print("Index", index)
                if page[index:index + 10] not in total_pages:
                    # For extracting the total number of pages
                    total_pages.append(page[
                                       index:index + 10])  # for example : page=2 so in order to get the total number of pages and iterate through it it goes from 1 till end of pages for pagination
        # print("Total Pages", total_pages)
        average_gross_list = []
        for num in range(1, len(total_pages) + 1, 1):
            try:
                url = 'https://www.boxofficemojo.com/people/?view=Actor&pagenum={}&sort=sumgross&order=DESC&&p=.htm'.format(num)  # This one works well
                # Get the Response
                print("Page number {}".format(num))
                response_from_url = requests.get(url)
                html = response_from_url.text
                soup = BeautifulSoup(html,
                                     'lxml')  # lxml is a pretty extensive library written for parsing XML and HTML documents very quickly
                table = soup.find('table', {"cellspacing": "1"})
                # Using dataframes
                df = pd.read_html(str(table),skiprows=1)
                df = df[0]

                df = df.iloc[:, :6]  # This is used to slice the dataframe to cut off the date sections.
                df.columns = ['rank', 'person', 'total gross', 'number of movies', 'Average', 'number 1 picture']
                df['id'] = ''

                id_list = []
                title_list = df['rank'].tolist()
                new_index = [i for i in range(1,len(title_list)+1)]
                df.index = new_index
                for link in soup.findAll('a', {'href': re.compile("\?id=")}):
                    id_list.append(link.get('href'))

                id_list = [x.split('=')[1] for x in id_list]
                id_list = [x.split('.')[0] for x in id_list]
                id_list = id_list[1:]
                id_dict = dict(zip(title_list, id_list))

                for index in df.index:
                    df.loc[index, 'id'] = id_dict[df.loc[index, 'rank']]

                df.to_csv("actors.csv", index=False, mode='a')

            except Exception as e:
                print(e)
                continue


        file_list = glob.glob("*.csv")
        df_container = []

        for file in file_list:
            df = pd.read_csv(file)
            df_container.append(df)

        df_combined = pd.concat(df_container)
        df_combined.to_csv("actors.txt", index=False, sep="\t")

        df = pd.read_csv("actors.txt", sep="\t")

        # Data Cleaning
        df['Average'] = df['Average'].apply(lambda x: x.replace('$', ''))  # replace dollar signs
        df['Average'] = df['Average'].apply(lambda x: x.replace(',', ''))  # replace commas

        df['Average'] = pd.to_numeric(df['Average'], errors='coerce')

        df = df.sort_values(by='Average', ascending=False)

        actor_with_highest_average_earning = df.iloc[0]['person']

        print("actor(s) with the highest average earnings per movie is {}".format(actor_with_highest_average_earning))
        new_df = pd.read_csv("actors.txt", sep="\t")

        new_df['number of movies'] = pd.to_numeric(new_df['number of movies'], errors='coerce')

        actor_most_movies = new_df.loc[new_df['number of movies'].idxmax()].person
        print("actor(s) with the maximum number of movies is {}".format(actor_most_movies))

if __name__ == '__main__':
 scrape_data_for_actors()
