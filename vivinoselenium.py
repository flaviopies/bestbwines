    # -*- coding: utf-8 -*-
    """ Created on Sat Jun 24 11:51:40 2017 @author: Flavio Pies """

    import datetime as dt
    import time
    import pandas as pd
    from selenium import webdriver
    from selenium.common.exceptions import TimeoutException
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.common.keys import Keys


    def openwebsite(url):
        browser.get(url)
        print("Page is ready!")
        delay = 10  # seconds
        try:
            WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.NAME, 'buy-buttons')))
        except TimeoutException:
            print("Loading took too much time")


    def extend_page():
        for i in range(100):
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

    def scrape_by_class(class_name):
        new_list = []
        infos = browser.find_elements_by_class_name(class_name)
        for info in infos:
            new_list.append(info.text)
        return new_list


    def get_shops_infos(button, silenced, button_class):
        close_pop_up()
        vendors = browser.find_elements_by_class_name("merchant-details")
        links = browser.find_elements_by_class_name("visit-shop")

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


    def close_pop_up():
        webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()


    def create_df(wines, wineries, locations, stats, button_class):
        new_list = []
        wait = WebDriverWait(browser, 10)
        problem_list = [[],[]]
        for i in range(len(wines)):
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
                infos = get_shops_infos2(0)
                print(infos)
                for j, info in enumerate(infos[2]):
                    new_list.append([wines[i], wineries[i], locations[i], stats[i], infos[0][j], infos[1][j], infos[2][j]])
                print("Success in scraping infos from line {}".format(i))
            except:
                print("Scraping problem in line {}".format(i))
                infos = ["","",""]
                new_list.append([wines[i], wineries[i], locations[i], stats[i], infos[0], infos[1], infos[2]])
                problem_list[1].append(i)
            print()
            close_pop_up()
            time.sleep(2)

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


    def prepare_df(df):
        df.columns = ["Name", "Winery", "Region", "Rating_info", "Vendor", "Price", "Link"]
        region_info = df.Region.str.split("\\n·\\n")
        df["Country"] = region_info.map(lambda x: x[0]).map(str)
        df["Region"] = region_info.map(lambda x: x[1]).map(str)
        rating_info = df.Rating_info.str.split("\\n")
        df["Rating"] = rating_info.map(lambda x: x[1]).map(float)
        df["Reviews"] = rating_info.map(lambda x: x[2]).str.strip(" ratings").map(int)
        df["Vendor"] = df.Vendor.str.split("\\n").map(lambda x: x[2]).map(str)
        df["Vendor_info"] = df.Vendor.str.split("\\n").map(lambda x:x[1])
        df["Vendor_location"] = df.Vendor.str.split("\\n").map(lambda x: x[3]).map(str).strip("Based in ").map(lambda x: x[1])
        df["Vendor_location"] = df.Vendor_location.str.strip("Based in")
        df.Price = df.Price.str.replace(",",".")
        df.Price = df.Price.str.strip("R$").map(float)
        return df

    # TODO function extend_page not working properly
    #extend_page()
    #extend_page()
    #extend_page()
    #extend_page()


    today = dt.datetime.today()
    browser = webdriver.Chrome()
    time.sleep(5)
    url = "https://www.vivino.com/explore"
    openwebsite(url)
    time.sleep(5)

    roll_page_down()

    wine_name_class = "wine-card__header__wine"
    winery_class = "wine-card__header__winery"
    location_class = "location"
    statistics_class = "wine-card__statistics"
    button_class = "add-to-cart-button"

    wines = scrape_by_class(wine_name_class)
    wineries = scrape_by_class(winery_class)
    locations = scrape_by_class(location_class)
    stats = scrape_by_class(statistics_class)

    df = create_df(wines,wineries,locations,stats,button_class)
    df = pd.DataFrame(df[0])
