    # -*- coding: utf-8 -*-
    """ Created on Sat Jun 24 11:51:40 2017 @author: Flavio Pies """

    import datetime as dt

    import pandas as pd
    from selenium import webdriver
    from selenium.common.exceptions import TimeoutException
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.common.keys import Keys


    today = dt.datetime.today()
    browser = webdriver.Chrome()

    url = "https://www.vivino.com/explore"

    def openwebsite(url):
        # Opens guiabolso page and waits loading time
        browser.get(url)
        print("Page is ready!")
        #delay = 10  # seconds
        #try:
        #    WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.NAME, 'buy-buttons')))
        #except TimeoutException:
            #print("Loading took too much time")

    def extend_page():
        for i in range(100):
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    #def choose_wine_type():
        #Interact with wine type

    #def choose_price_range():
        #interact with pricing bands

    #def choose_rating_range():
        #def rating range

    def scrape_by_class(class_name):
        new_list = []
        infos = browser.find_elements_by_class_name(class_name)
        for info in infos:
            new_list.append(info.text)
        return new_list


    def get_shops_infos(button, silenced):
        close_pop_up()
        wait = WebDriverWait(browser, 10)
        try:
            wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'buy-button')))
            button.click()

        except:
            print("TimeoutException")

        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "merchant-details")))
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "view-shop-button")))

        vendors = browser.find_elements_by_class_name("merchant-details")
        links = browser.find_elements_by_class_name("view-shop-button")

        suppliers_list = []
        prices_list = []
        links_list = []
        for link_i, link in enumerate(links):
            try:
                vendor = vendors[link_i].text
                price = links[link_i].text
                link_url = links[link_i].get_attribute("href")

                suppliers_list.append(vendor)
                prices_list.append(price)
                links_list.append(link_url)

                if not silenced:
                    print("Vendor {} selling for {} at link: {}".format(vendor,price,link_url))
            except:
                print("Error in {} interaction".format(link_i))
        #close_shop_infos():
        output = suppliers_list, prices_list, links_list
        try:
            close_pop_up()
        except:
            print("Error in closing vendor list")
            output = 0
        return output



    def shops_infos_old(button, silenced):
        button.click()
        links = browser.find_elements_by_class_name("visit-shop")
        #ideia é fazer a cada duplas
        suppliers_list = []
        prices_list = []
        links_list = []
        for link_i in range(int(len(links)/2)):
            try:
                if not silenced: print(links[int(link_i * 2)].text,links[int(link_i * 2 + 1)].text,links[int(link_i * 2)].get_attribute("href"))
                #browser.find_element_by_class_name("merchant-details").text
                #browser.find_element_by_class_name("view-shop-button").text
                #browser.find_element_by_class_name("view-shop-button").get_attribute("href")
                suppliers_list.append(links[int(link_i * 2)].text)
                prices_list.append(links[int(link_i * 2) + 1].text)
                links_list.append(links[int(link_i * 2)].get_attribute("href"))
            except:
                print("Error in {} interaction".format(link_i))
        #close_shop_infos():
        output = suppliers_list, prices_list, links_list
        try:
            close_pop_up()
        except:
            print("Error in closing vendor list")
            output = 0
        return output


    def close_pop_up():
        webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()


    def create_df(wines, wineries, locations, stats, buybuttons):
        new_list = []
        for i,buybutton in enumerate(buybuttons):
            infos = get_shops_infos(buybutton, 0)
            for j, info in enumerate(infos[0]):
                new_list.append([wines[i],wineries[i],locations[i],stats[i],infos[0][j],infos[1][j],infos[2][j]])
        return new_list

    openwebsite(url)

    # TODO function extend_page not working properly
    #extend_page()
    #extend_page()
    #extend_page()
    #extend_page()

    wine_name_class = "wine-card__header__wine"
    winery_class = "wine-card__header__winery"
    location_class = "location"
    statistics_class = "wine-card__statistics"
    button_class = "buy-button"

    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, wine_name_class)))
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, winery_class)))
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, location_class)))
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, statistics_class)))
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, button_class)))

    wines = scrape_by_class(wine_name_class)
    wineries = scrape_by_class(winery_class)
    locations = scrape_by_class(location_class)
    stats = scrape_by_class(statistics_class)
    buybuttons = browser.find_elements_by_class_name(button_class)

    df = create_df(wines,wineries,locations,stats,buybuttons)