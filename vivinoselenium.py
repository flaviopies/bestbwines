# -*- coding: utf-8 -*-

import datetime as dt
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import numpy as np
import re

def openwebsite(url):
    browser.get(url)
    print("Page is ready!")


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


def translate_class_to_rating(rating_class):
    rating = rating_class.replace("icon-","")
    rating = rating.replace("-pct", "")
    rating = float(rating)/100
    return rating


def wine_main_page_scrape(wine_name, winery_name ,wine_url, scrape_general_info = 1, scrape_merchants = 1,scrape_previous_years = 1,scrape_comments = 1):

    browser.get(wine_url)
    #WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "page__header__information__details__location__region")))

    if scrape_general_info:
        #General infos - related to wine table
        region = browser.find_element_by_class_name("wine-page__header__information__details__location__region").text
        country = browser.find_element_by_class_name("wine-page__header__information__details__location__country").text
        n_ratings = browser.find_element_by_class_name("wine-page__header__information__details__average-rating__label").text
        rating = browser.find_element_by_class_name("wine-page__header__information__details__average-rating__value__number").text
        price_avg = browser.find_element_by_class_name("wine-page__header__information__details__average-price__label--highlight").text
        highlights = browser.find_elements_by_class_name("highlights__wrapper")
        highlights = "".join(x.text + "\n" for x in highlights)
        wine_type = browser.find_element_by_class_name("wine-selector__middle").text

        #summary infos - related to wine table
        grape, regional_style, food_pairing = "","",""
        try:
            summary_info = browser.find_elements_by_class_name("wine-page__summary__item__content")
            grape = summary_info[1].text
            regional_style = summary_info[3].text
            food_pairing = summary_info[4].text
        except:
            pass

        general_info_list = [wine_name, winery_name, wine_type, region, country, n_ratings, rating, price_avg, highlights, grape, regional_style, food_pairing]
        general_info_df = pd.DataFrame(data=[general_info_list],
                                       columns=["Name","Winery","Type","Region","Country","N_ratings","Rating","Price","Highlights","Grape","Regional_style","Food_pairing"])
        if not general_info_df.empty:
            print("Succesfully created general_info_df for {}".format(wine_name))
    else:
        general_info_df = ""
        print("Didn't create general_info_df for {}".format(wine_name))

    if scrape_merchants:
        #Press vendor button - related to vendor table
        merchant_infos_list = [[], [], [], [], [], [], []]
        shop_button = browser.find_element_by_class_name("show-merchants")
        try:
            shop_button.click()
            try:
                show_all_merchants = WebDriverWait(browser, 3).until(EC.element_to_be_clickable((By.CLASS_NAME, "show-all-merchants")))
                browser.execute_script("arguments[0].scrollIntoView();", show_all_merchants)
                show_all_merchants.click()
            except:
                print("Didn't find 'show_all_merchants' link")

            merchants_infos_elements = WebDriverWait(browser, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ppc-merchant-shop")))
            #merchants_infos_elements = browser.find_elements_by_class_name("ppc-merchant-shop")
            for merchants_infos in merchants_infos_elements:
                merchant_infos_list[0].append(wine_name)
                merchant_infos_list[1].append(winery_name)
                try:
                    merchant_infos_list[2].append(merchants_infos.find_element_by_class_name("visit-shop").text)
                except:
                    merchant_infos_list[2].append("")
                try:
                    merchant_infos_list[3].append(merchants_infos.find_element_by_class_name("merchant-description").text)
                except:
                    merchant_infos_list[3].append("")
                try:
                    merchant_infos_list[4].append(merchants_infos.find_element_by_class_name("wine-country").text)
                except:
                    merchant_infos_list[4].append("")
                try:
                    merchant_infos_list[5].append(merchants_infos.find_element_by_class_name("merchant-link").text)
                except:
                    merchant_infos_list[5].append("")
                try:
                    merchant_infos_list[6].append(merchants_infos.find_element_by_class_name("view-shop-button").get_attribute("href"))
                except:
                    merchant_infos_list[6].append("")
        except:
            merchant_infos_list = [wine_name,winery_name,[], [], [], [], []]

        merchant_df = pd.DataFrame(columns=["Name","Winery","Merchant","Merchant_description","Country_merchant","Price","Link_merchant"])
        for i, col in enumerate(merchant_df.columns):
            merchant_df[col] = merchant_infos_list[i]

        if not merchant_df.empty:
            print("Succesfully created merchant_df for {}".format(wine_name))
        else:
            print("Merchant_df is empty for {}".format(wine_name))
    else:
        merchant_df = ""
        print("Didn't create merchant_df for {}".format(wine_name))

    if scrape_previous_years:
        #previous_years
        try:
            show_previous_year_button = WebDriverWait(browser, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "vintage-comparison__actions")))
            browser.execute_script("arguments[0].scrollIntoView();", show_previous_year_button )
            show_previous_year_button = show_previous_year_button.find_element_by_css_selector("a")
            show_previous_year_button.click()
        except:
            print("It seems this wine is particularly young ...")
        previous_years_list = []
        previous_years = browser.find_elements_by_class_name("vintage-comparison__item__year")
        for year in previous_years:
            previous_years_list.append(year.text)

        previous_years_ratings_list = []
        previous_years_ratings = browser.find_elements_by_class_name("vintage-comparison__item__statistics__count")
        for rating in previous_years_ratings:
            previous_years_ratings_list.append(rating.text)

        previous_years_n_ratings_list = []
        previous_years_n_ratings = browser.find_elements_by_class_name("vintage-comparison__item__statistics__rating")
        for n_rating in previous_years_n_ratings:
            previous_years_n_ratings_list.append(n_rating .text)

        wine_name_list = [wine_name for year in previous_years_list]
        winery_name_list = [winery_name for year in previous_years_list]
        previous_years_infos = [wine_name_list,winery_name_list ,previous_years_list,previous_years_ratings_list,previous_years_n_ratings_list]

        previous_years_df = pd.DataFrame(columns=["Name","Winery","Year","Rating","N_ratings"])
        for i, col in enumerate(previous_years_df .columns):
            previous_years_df[col] = previous_years_infos[i]

        if not previous_years_df.empty:
            print("Succesfully created previous_year_df for {}".format(wine_name))

    else:
        previous_years_df = ""
        print("Didn't create previous_year_df for {}".format(wine_name))

    if scrape_comments:
        #comments
        test_i = 0
        for _ in range(10000):
            try:
                element = WebDriverWait(browser, 3).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "vintage-review-items__show-more")))
                browser.execute_script("arguments[0].scrollIntoView();", element)
                element.click()
                print("It worked")
                test_i = 0
            except:
                print("Didn't work")
                test_i = test_i + 1
                if test_i > 5:
                    break

        user_info_selenium = browser.find_elements_by_class_name("vintage-review-item__content")
        user_infos = [[],[]]
        for info in user_info_selenium:
            try:
                user_infos[0].append(info.find_element_by_class_name("information__name").text)
            except:
                user_infos[0].append("")
            try:
                user_infos[1].append(info.find_element_by_class_name("vintage-review-item__content__note").text)
            except:
                user_infos[1].append("")

        selenium_element_ratings = browser.find_elements_by_class_name("vintage-review-item__rating")
        ratings_from_users = []
        for rating_element in selenium_element_ratings:
            sum = 0
            for rev in rating_element.find_elements_by_css_selector("*"):
                sum = sum + translate_class_to_rating(rev.get_attribute("class"))
            ratings_from_users.append(sum)

        user_infos[2] = ratings_from_users
        user_infos[3] = [wine_name for rating in ratings_from_users]
        user_infos[4] = [winery_name for rating in ratings_from_users]
        comments_df = pd.DataFrame(columns=["User_info","Comment","Rating","Name","Winery"])
        for i, col in enumerate(comments_df.columns):
            comments_df[col] = user_infos[i]
    else:
        comments_df = ""
        print("Didn't create comments_df for {}".format(wine_name))

    #Missing scraping recommended wines

    return general_info_df, merchant_df, previous_years_df, comments_df


if __name__ == "__main__":
    today = dt.datetime.today()
    browser = webdriver.Chrome()
    time.sleep(5)
    url = "https://www.vivino.com/explore"
    openwebsite(url)
    time.sleep(5)

    wine_type_class = "wine-type-selector__item"
    wine_name_class = "wine-card__header__wine"
    wine_links_class = "wine-card__header"
    winery_class = "wine-card__header__winery"
    button_class = "add-to-cart-button"
    slider_class = "ui-slider-handle"

    sliders = browser.find_elements_by_class_name(slider_class)
    # Set price range to maximum
    #ActionChains(browser).click_and_hold(sliders[0]).move_by_offset(-50,0).release().perform()
    ActionChains(browser).click_and_hold(sliders[1]).move_by_offset(120,0).release().perform()
    # Set ratings range to maximum
    #ActionChains(browser).click_and_hold(sliders[2]).move_by_offset(-40,0).release().perform()
    #select all wine_types
    wine_type_buttons = browser.find_elements_by_class_name(wine_type_class)[1:]
    for type_button in wine_type_buttons:
        type_button.click()
    time.sleep(10)

    roll_page_down()
    wines = scrape_by_class(wine_name_class)
    wineries = scrape_by_class(winery_class)
    wine_links = [element.get_attribute("href") for element in browser.find_elements_by_class_name(wine_links_class)]
    all_wines_list = [wines,wineries,wine_links]

    all_wines_df = pd.DataFrame(columns=["Wine","Winery","Wine_url"])
    for i, col in enumerate(all_wines_df.columns):
        all_wines_df[col] = all_wines_list[i]

    time.sleep(3)
    all_wines_df.to_excel("20171014_All_wines.xlsx")

    try:
        wine_df = pd.read_excel("20171014_Wines.xlsx")
    except:
        wine_df = pd.DataFrame()

    try:
        merchant_df = pd.read_excel("20171014_Merchants.xlsx")
    except:
        merchant_df = pd.DataFrame()

    try:
        previous_year_df = pd.read_excel("20171014_Previous_years.xlsx")
    except:
        previous_year_df = pd.DataFrame()

    try:
        comments_df = pd.read_excel("20171014_Comments.xlsx")
    except:
        comments_df = pd.DataFrame()

    loop_start_time = time.time()
    for idx, wine in enumerate(wines):

        if wine not in wine_df["Name"].values:
            start_time = time.time()
            try:
                wine_temp, merchant_temp, previous_year_temp , comments_temp =wine_main_page_scrape(wines[idx],wineries[idx],wine_links[idx],1,1,1,0)
            except:
                print("Failed in scraping {}".format(wine))
            end_time = time.time()

            try:
                wine_df = pd.concat([wine_df,wine_temp],axis=0)
                print("Added information to wine_df")
            except:
                print("Didn't add information to wine_df")
                pass
            try:
                merchant_df = pd.concat([merchant_df,merchant_temp],axis=0)
                print("Added information to merchant_df")
            except:
                print("Didn't add information to merchant_df")
                pass
            try:
                previous_year_df = pd.concat([previous_year_df,previous_year_temp],axis=0)
                print("Added information to previous_year_df")
            except:
                print("Didn't add information to previous_year_df")
                pass
            try:
                comments_df = pd.concat([comments_df,comments_temp],axis=0)
                print("Added information to comments_df")
            except:
                print("Didn't add information to comments_df")
                pass

            print()
            print("Scraping {} took {} seconds".format(wine, end_time - start_time))
            print("Running {} iteration of {} - {} seconds passed".format(idx+1, len(wines), end_time - loop_start_time))
            print()
        else:
            print("Wine {} has already been scraped".format(wine))
            pass

    time.sleep(5)
    try:
        wine_df.to_excel("20171014_Wines.xlsx")
        print("Exporting wines_df in Excel")
    except:
        print("Problem in exporting wines_df in Excel")
    try:
        merchant_df.to_excel("20171014_Merchants.xlsx")
        print("Exporting merchants_df in Excel")
    except:
        print("Problem in exporting merchant_df in Excel")
    try:
        previous_year_df.to_excel("20171014_Previous_years.xlsx")
        print("Exporting previous_year_df in Excel")
    except:
        print("Problem in exporting previous_year_df in Excel")
    try:
        comments_df.to_excel("20171014_Comments.xlsx")
        print("Exporting comments_df in Excel")
    except:
        print("Problem in exporting comments_df in Excel")



