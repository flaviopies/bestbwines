import requests
import re
import pandas as pd
from bs4 import BeautifulSoup

site = "https://www.wine.com.br/vinhos/tinto/cVINHOS-atTIPO_TINTO-p1.html"

def wine_request(site,page):
    r = requests.get(site,{"pn": page})
    if r.status_code == 200:
        output = r
        print("Request successful")
    else:
        output = r.status_code
        print("Request failed")
    return output


def wine_soup(r):
    soup = BeautifulSoup(r.text,"html.parser")
    return soup


def find_wine_names(soup):
    wine_names_list = []
    name_list = soup.select(".barraTitulo")
    for name in name_list:
        wine_names_list.append(name.h2.a.string)
    return wine_names_list


def find_wine_description(soup):
    wine_description_list = [[],[],[],[],[]]
    description_list = soup.select(".descProdutos")
    for description in description_list:
        wine_description_list[0].append(description.ul.li.strong.string)
        wine_description_list[1].append(description.ul.li.span.string.split(", ")[0])
        wine_description_list[2].append(description.ul.li.span.string.split(", ")[1])
        wine_type_vol = description.ul.li.next_sibling.next_sibling.strong.string
        wine_type_vol = re.sub('[\t\n+]', '', wine_type_vol)
        wine_type_vol = wine_type_vol.split("- ")
        wine_description_list[3].append(wine_type_vol[0])
        wine_description_list[4].append(wine_type_vol[1])
    return wine_description_list


def find_wine_prices(soup):
    wine_price_list = []
    price_list = soup.select(".boxPreco")
    for price in price_list:
        price_value = price.p.strong.span.next_sibling.string
        wine_price_list.append(price_value.strip(" "))
    return wine_price_list


def pagination_dataframe(site, n_max):
    df = pd.DataFrame()
    pages_iteration = range(1, n_max)

    for page in pages_iteration:
        try:
            temp_df = pd.DataFrame()
            r = wine_request(site, page)
            soup = wine_soup(r)
            temp_df["Names"] = find_wine_names(soup)  # names
            temp_df["Winery"] = find_wine_description(soup)[0]  # winery
            temp_df["Region"] = find_wine_description(soup)[1]  # region
            temp_df["Country"] = find_wine_description(soup)[2]  # country
            temp_df["Type"] = find_wine_description(soup)[3]  # type
            temp_df["Volume"] = find_wine_description(soup)[4]  # volume
            temp_df["Price"] = find_wine_prices(soup)  # price
            df = pd.concat([df,temp_df],axis=0)
            del temp_df
        except:
            print("Exception on page {}".format(page))

    return df


def last_page(soup):
    nav_list = soup.select(".navegacaoListagem")
    last = nav_list [0].ul.find_all("li")[-2].a.string
    return last