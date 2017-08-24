import vivinocrawler
import winecrawler
from datetime import datetime as dt

site = "https://www.wine.com.br/vinhos/tinto/cVINHOS-atTIPO_TINTO-p1.html"

def create_df(site):
    wine_request = winecrawler.wine_request(site,1)
    wine_soup = winecrawler.wine_soup(wine_request)
    lastpage = winecrawler.last_page(wine_soup, 1)
    df = winecrawler.pagination_dataframe(site,lastpage)
    return df

def date_today(date):
    return date.year.__str__() + date.month.__str__() + date.day.__str__()

def create_csv(df,dir,date):
    try:
        df.to_csv(address + date + ".csv")
        print("Success in exporting as csv")
        success = 1
    except:
        print("Failure in exporting as csv")
        success = 0
    return success

df = create_df(site)
wine_list = vivino_rating_iterator(df.Names)
df["Rating"] = wine_list[0]
df["Nb_reviews"] = wine_list[1]

dir = "PUT YOUR DIR HERE"
success = create_csv(df,dir,date_today(dt.today()))
