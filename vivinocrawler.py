import requests
import re
import pandas as pd
from bs4 import BeautifulSoup
import configparser

#configParser = configparser.RawConfigParser()
#configFilePath = r"config"
#configParser.read(configFilePath)
#user_agent = configParser.get('your-config', 'user_agent')

url = 'https://www.vivino.com/search/wines?q=Toro+loco+2015&start=1'

def vivino_simple_request(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        output = r
        print("Request successful")
    else:
        output = r.status_code
        print("Request failed")
    return output


def vivino_request(vivino_site,user_agent,search):
    headers = {
        'User-Agent': user_agent,
        "q": search
        }
    r = requests.get(vivino_site, headers=headers)
    if r.status_code == 200:
        output = r
        print("Request successful")
    else:
        output = r.status_code
        print("Request failed")
    return output


def vivino_soup(r):
    soup = BeautifulSoup(r.text,"html5lib")
    return soup


def url_replace(url,wine):
    url = url.replace("Toro+loco+2015",wine)
    url = url.replace(" ","+")
    return url


def vivino_rating(soup):
    text = re.sub("[\n+]", "", soup.select(".text-inline-block.light.average__number")[0].string)
    text = text.replace(",",".")
    rating = float(text)
    return rating


def vivino_rating_n(soup):
    text = soup.select(".text-micro")[0].string.replace(" ratings","").replace("\n","")
    number_ratings = float(text)
    return number_ratings


def vivino_rating_iterator(wine_list):
    rating_list = []
    n_list = []
    for n, wine in enumerate(wine_list):
        new_url = url_replace(url, wine)
        new_r = vivino_simple_request(new_url)
        new_soup = vivino_soup(new_r)
        try:
            rating = vivino_rating(new_soup)
            rating_n = vivino_rating_n(new_soup)
            print("{} - Rating: {}, number of reviews: {},- iteração {} de {}".format(wine,rating,rating_n,n,len(wine_list)))
        except:
            rating = "No rating available"
            rating_n = "No rating available"
            print("Problems in scrapping {} - iteração {} de {}".format(wine,n,len(wine_list)))
        rating_list.append(rating)
        n_list.append(rating_n)
    return [rating_list,n_list]

