import vivinocrawler
import winecrawler

site = "https://www.wine.com.br/vinhos/tinto/cVINHOS-atTIPO_TINTO-p1.html"

wine_request = winecrawler.wine_request(site,1)
wine_soup = winecrawler.wine_soup(wine_request)
lp = winecrawler.last_page(wine_soup )
df = winecrawler.pagination_dataframe(site,int(lp))

rating_list = []
wine_list = df["Names"].values
url = 'https://www.vivino.com/search/wines?q=Toro+loco+2015&start=1'

