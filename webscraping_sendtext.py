#Online References used :

#https://github.com/imadmali/movie-scraper/blob/master/MojoLinkExtract.py
#https://www.crummy.com/software/BeautifulSoup/bs4/doc/
#https://nycdatascience.com/blog/student-works/scraping-box-office-mojo/
#https://www.youtube.com/watch?v=XQgXKtPSzUI
# https://www.youtube.com/watch?v=aIPqt-OdmS0
#https://www.youtube.com/watch?v=XQgXKtPSzUI
from bs4 import BeautifulSoup
import pandas as pd
import os
import requests
import glob
import re


class WebScrapping:

    def __init__(self, url, user_input):
        self.url = url
        self.user_input = user_input
        self._scrape_data_for_movies()

    def _scrape_data_for_movies(self):
        file_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')#This is written in order to save the txt file in the user's specified location on the machine
        file_path = os.path.join(file_path, 'BoxOfficeMojo_4428vs')#Folder name to be created where the file will be stored
        if not os.path.exists(str(file_path)):
            os.mkdir(str(file_path))#If path does not exist create the path
        os.chdir(file_path)#Change the directory of the file path

        if len(glob.glob("*")) != 0: #The glob module finds all the pathnames matching a specified pattern according to the rules used by the Unix shell
            file_list = glob.glob("*")
            for file in file_list:
                os.remove(file)

        #The url of the BoxOffice Mojo to be scraped
        url = 'https://www.boxofficemojo.com/yearly/chart/?page={}&view=releasedate&view2=domestic&yr={}&p=.htm'.format(
            1, user_input)
        pages_data = [] #List to store the pages data
        total_pages = []
        response = requests.get(url) # Get the response of the url after passing the user input
        soup = BeautifulSoup(response.content, 'html.parser')# Using the beautiful soup library to parse the html content and format it
        for page in soup.find_all('a', href=lambda href: href and "page" in href): #find the href in a tags
            pages_data.append(page['href'])#append the data in the pages_data list
        for page in pages_data:
            if 'page' in page: #If "page" found in href
                index = page.find('page')#Take the index of that page if found
                if page[index:index + 6] not in total_pages:
                    #For extracting the total number of pages
                    total_pages.append(page[index:index + 6]) #for example : page=2 so in order to get the total number of pages and iterate through it it goes from 1 till end of pages for pagination
        for num in range(1, len(total_pages) + 1, 1):
            try:
                url = 'https://www.boxofficemojo.com/yearly/chart/?page={}&view=releasedate&view2=domestic&yr={}&p=.htm'.format(
                    num, user_input)  # This one works well
                print("Page number {} for the year{}".format(num, user_input))
                #Get the Response
                response_from_url = requests.get(url)
                html = response_from_url.text
                soup = BeautifulSoup(html, 'lxml')# lxml is a pretty extensive library written for parsing XML and HTML documents very quickly
                table = soup.find('table', {"cellspacing": "1"})
                #Using dataframes
                df = pd.read_html(str(table), skiprows=2)
                df = df[0]
                df = df.iloc[:, :7]  # This is used to slice the dataframe to cut off the date sections.

                # headers = df.dtypes.index For getting the columnn names

                df.columns = ['rank', 'title', 'studio', 'total gross', 'total theaters', 'opening gross', 'opening theaters']
                df = df[:len(df.index) - 3]
                df = df[['title', 'studio', 'total gross', 'total theaters', 'opening gross', 'opening theaters']]

                df['id'] = ''  #Use to get the id's of the movies

                id_list = []
                title_list = df['title'].tolist()

                for link in soup.findAll('a', {'href': re.compile("\?id=")}):  # Getting the ids
                    id_list.append(link.get('href'))  # Adding the movie id to the list

                id_list = [x.split("=")[1] for x in id_list]  # isolating the id 1
                id_list = [x.split(".")[0] for x in id_list]  # isolating the id 2
                id_list = id_list[
                          1:]  # cutting off the first entry (first entry gives the #1 box office entry for the current week).
                id_dict = dict(zip(title_list, id_list))

                for index in df.index:
                    df.loc[index, 'id'] = id_dict[df.loc[index, 'title']]#For all the indexes in the movie list

                df.to_csv("{}-{}.csv".format(user_input, num), index=False)

            except ValueError:
                print("Please enter a valid url or a value that can be parsed")
                continue

        #Conversion of txt file to csv
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

        # Data Cleaning
        df['total gross'] = df['total gross'].apply(lambda x: x.replace('$', ''))  # replace dollar signs
        df['total gross'] = df['total gross'].apply(lambda x: x.replace(',', ''))  # replace commas
        df['total gross'] = df['total gross'].apply(lambda x: int(x))  # conversion from string to int

        # Formatting $ value - See here: https://stackoverflow.com/questions/21208376/converting-float-to-dollars-and-cents
        avg_total_gross_earnings = '${:,.2f}'.format(df['total gross'].mean())

        df = df.sort_values(by='total theaters', ascending=False)  # sorting the dataframe to get the highest number of theatres where the movie was shown.

        max_number_theatres = df.iloc[0]['title']
        total_theatres_max = int(df.iloc[0]['total theaters'])#Getting the maximum number of theatres where the movie was shown

        print("----------RESULT---------------")
        print("The Average Total Gross Earnings for the year {} is {}".format(user_input, avg_total_gross_earnings))
        print("The Movie that was shown in the most theaters was '{}' with {} theaters".format(max_number_theatres,
                                                                                               total_theatres_max))
if __name__ == '__main__':
    user_input = input('What is the year that you are interested in getting data:')
    url = 'https://www.boxofficemojo.com/yearly/chart/?page=1&view=releasedate&view2=domestic&yr=' + user_input + '&p=.htm'
    web_scrapping_object = WebScrapping(url=url, user_input=user_input)