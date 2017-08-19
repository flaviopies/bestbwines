import requests
from bs4 import BeautifulSoup

site_tinto = 'https://www.wine.com.br/vinhos/tinto/cVINHOS-atTIPO_TINTO-p1.html'
site_branco = "https://www.wine.com.br/vinhos/branco/cVINHOS-atTIPO_BRANCO-p1.html"
site_rose = "https://www.wine.com.br/vinhos/rose/cVINHOS-atTIPO_ROSE-p1.html"
site_espumante = "https://www.wine.com.br/vinhos/espumante/cVINHOS-atTIPO_ESPUMANTE-p1.html"
site_licoroso = "https://www.wine.com.br/vinhos/licoroso/cVINHOS-atTIPO_LICOROSO-p1.html"

site = site_tinto
def wine_request(site):
    r = requests.get(site)
    if r.status_code = 200:
        output = r.text
    else
        output = r.status_code
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
    wine_description_list = [[],[],[]]
    description_list = soup.select(".descProdutos")
    for description in description_list:
        wine_description_list[0].append(description.ul.li.strong.string)
        wine_description_list[1].append(description.ul.li.span.string.split(", "))
        wine_type_vol = description.ul.li.next_sibling.next_sibling.strong.string
        wine_type_vol = re.sub('[\t\n+]', '', wine_type_vol)
        wine_type_vol = wine_type_vol.split("- ")
        wine_description_list[2].append(wine_type_vol)
    return wine_description_list

def find_wine_prices(soup):
    wine_price_list = []
    price_list = soup.select(".boxPreco")
    for price in price_list:
        price_value = price.p.strong.span.next_sibling.string
        wine_price_list.append(price_value.strip(" "))
    return wine_price_list