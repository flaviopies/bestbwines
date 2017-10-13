# -*- coding: utf-8 -*-

import datetime as dt
import time
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import numpy as np

def openwebsite(url):
    browser.get(url)
    print("Page is ready!")
    delay = 10  # seconds
    #try:
    #    WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.NAME, 'add-to-cart-button')))
    #except TimeoutException:
    #    print("Loading took too much time")


def extend_page():
    for _ in range(100):
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

#def choose_wine_type():
    #Interact with wine type

#def choose_price_range():
    #interact with pricing bands

#def choose_rating_range():
    #def rating range


def roll_page_down():
    SCROLL_PAUSE_TIME = 0.5

    # Get scroll height
    last_height = browser.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def go_to_home():
    SCROLL_PAUSE_TIME = 0.5
    browser.execute_script("window.scrollTo(0, 0);")
    # Wait to load page
    time.sleep(SCROLL_PAUSE_TIME)


def scrape_by_class(class_name):
    new_list = []
    infos = browser.find_elements_by_class_name(class_name)
    for info in infos:
        new_list.append(info.text)
    return new_list


def close_pop_up():
    webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()


def create_df(wines, wineries, locations, stats, button_class, winetype):
    new_list = []
    wait = WebDriverWait(browser, 10)
    problem_list = [[],[]]
    for i in range(len(wines)):
        close_pop_up()
        time.sleep(2)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "add-to-cart-button")))
        #TODO Correct always loading the buttons, instead bring them as argument similar to "wines"
        buybuttons = browser.find_elements_by_class_name(button_class)
        try:
            print("Button {} clicked".format(i))
            buybuttons[i].click()
            time.sleep(1)
            print("Success in button clicking")

        except:
            print("Button problem in line {}".format(i))
            problem_list[0].append(i)
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "view-shop-button")))
            infos = get_shops_infos(0)
            print(infos)
            for j, info in enumerate(infos[2]):
                new_list.append([wines[i], wineries[i], locations[i], stats[i], infos[0][j], infos[1][j], infos[2][j],winetype])
            print("Success in scraping infos from line {}".format(i))
        except:
            print("Scraping problem in line {}".format(i))
            infos = ["","",""]
            new_list.append([wines[i], wineries[i], locations[i], stats[i], infos[0], infos[1], infos[2],winetype])
            problem_list[1].append(i)
        print()

    return new_list, problem_list


def get_shops_infos(silenced):

    vendors = browser.find_elements_by_class_name("merchant-details")
    #links = browser.find_elements_by_class_name("view-shop-button")
    links = browser.find_elements_by_class_name("view-shop-button")

    suppliers_list = []
    prices_list = []
    links_list = []

    for link_i, link in enumerate(links):
        vendor = vendors[link_i].text
        price = links[link_i].text
        link_url = links[link_i].get_attribute("href")

        suppliers_list.append(vendor)
        prices_list.append(price)
        links_list.append(link_url)

        if not silenced:
            print("Vendor {} selling for {} at link: {}".format(vendor,price,link_url))

    output = suppliers_list, prices_list, links_list
    return output


def vendor_info(info,i):
    try:
        return info.split("\\n")[i]
    except:
        return ""


def vendor_location(info,i):
    try:
        return info.split("Based in ")[i]
    except:
        return ""


def create_html_link(names,links):
    output = []
    for i, name in enumerate(names):
        link = links[i]
        html_link = '<a href="{}">{}</a>'.format(link,name)
        output.append(html_link)
    return output


def prepare_df(df):
    df.columns = ["Name", "Winery", "Region", "Rating_info", "Vendor", "Price", "Link","Wine_type"]
    df['Price'].replace('', np.nan, inplace=True)
    df = df.dropna(how="any")
    df["Region"] = df.Region.str.split("\\n·\\n")
    df[["Country", "Region"]] = pd.DataFrame(df.Region.values.tolist())
    rating_info = df.Rating_info.str.split("\\n")
    df["Rating"] = rating_info.map(lambda x: x[1]).map(float)
    df["Reviews"] = rating_info.map(lambda x: x[2]).str.strip(" ratings").map(int)
    df["Vendor_name"] = df.Vendor.map(lambda x: vendor_info(x,0))
    df["Vendor_info"] = df.Vendor.map(lambda x: vendor_info(x,0))
    df["Vendor_location"] = df.Vendor.map(lambda x: vendor_location(x,1))
    df["Price"] = df.Price.str.replace(",",".")
    df["Price"] = df.Price.str.strip("R$").map(float)
    df["Html_link"] = create_html_link(df.Name.values,df.Link.values)
    return df


def select_wine_type(activebutton,buttontoactivate):
    activebutton.click()
    time.sleep(2)
    buttontoactivate.click()
    winetype = buttontoactivate.text
    time.sleep(2)
    return winetype


today = dt.datetime.today()
browser = webdriver.Chrome()
time.sleep(5)
url = "https://www.vivino.com/explore"
openwebsite(url)
time.sleep(5)


wine_type_class = "wine-type-selector__item"
wine_name_class = "wine-card__header__wine"
winery_class = "wine-card__header__winery"
location_class = "location"
statistics_class = "wine-card__statistics"
button_class = "add-to-cart-button"
slider_class = "ui-slider-handle"

sliders = browser.find_elements_by_class_name(slider_class)
# Set price range to maximum
ActionChains(browser).click_and_hold(sliders[0]).move_by_offset(-30,0).release().perform()
ActionChains(browser).click_and_hold(sliders[1]).move_by_offset(50,0).release().perform()
# Set ratings range to maximum
ActionChains(browser).click_and_hold(sliders[2]).move_by_offset(-150,0).release().perform()
time.sleep(10)

roll_page_down()

wines = scrape_by_class(wine_name_class)
wineries = scrape_by_class(winery_class)
locations = scrape_by_class(location_class)
stats = scrape_by_class(statistics_class)

wine_type_buttons = browser.find_elements_by_class_name(wine_type_class)

df = create_df(wines, wineries, locations, stats, button_class,wine_type_buttons[0].text)
df = pd.DataFrame(df[0])
df = prepare_df(df)
close_pop_up()

for index, wine_type in enumerate(wine_type_buttons):
    try:
        if index < len(wine_type_buttons) -1:
            select_wine_type(wine_type_buttons[index],wine_type_buttons[index + 1])
            print("Scraping {} wines now ...".format(wine_type_buttons[index + 1].text))

            roll_page_down()
            time.wait(5)
            wines = scrape_by_class(wine_name_class)
            wineries = scrape_by_class(winery_class)
            locations = scrape_by_class(location_class)
            stats = scrape_by_class(statistics_class)

            dff = create_df(wines, wineries, locations, stats, button_class, wine_type.text)
            dff = pd.DataFrame(dff[0])
            dff = prepare_df(dff)
            df = pd.concat([df,dff],axis=0)
            close_pop_up()
            go_to_home()
    except:
        print("Couldn't scrape from {} to {} wine".format(wine_type_buttons[index].text,wine_type_buttons[index + 1].text))
        continue