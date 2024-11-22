# Web scraping project for Nico Exp Fitness Pitch
# Written by: Drake Adams
# 2/7/2024
# Sources:
# 1. https://github.com/SeleniumHQ/seleniumhq.github.io/blob/trunk/examples/python/tests/getting_started/first_script.py#L8


import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


def get_data_cb(driver):
    """[location name, address, status (open, closed, coming soon), # of classes per week, 4 class price, 8 class price,
     unlimited price, 5 pack price, 10 pack price]"""
    wait = WebDriverWait(driver, 10)
    data = []
    # Title
    data.append(driver.title.split("|")[0].strip())

    # Address
    address_container = driver.find_element(By.CLASS_NAME, "location-info-map__info")
    address_spans = address_container.find_elements(By.XPATH, ".//span[not(contains(@style, 'display:none'))]")
    address_parts = [span.text for span in address_spans if span.text.strip() != '']
    data.append(', '.join(address_parts[1:]))

    # Status (open -> at least 1 class this week, coming soon -> indicated on website, closed -> neither)
    # Number of Classes
    try:
        driver.find_element(By.CSS_SELECTOR, ".location-hero__ribbon.hero__ribbon--pinned")
        data.append("coming soon")
        for i in range(7):
            data.append("N/A")
        return data
    except NoSuchElementException:
        loc_div = driver.find_element(By.ID, "location-scheduler")
        day_list = loc_div.find_element(By.CSS_SELECTOR, ".table.location-scheduler__days")
        day_buttons = day_list.find_elements(By.TAG_NAME, 'button')
        class_count = 0
        for day in day_buttons:
            day.click()
            try:
                scheduler = driver.find_element(By.CSS_SELECTOR, ".table.location-scheduler__list")
                class_count += len(scheduler.find_elements(By.CLASS_NAME, "location-scheduler__class-row"))
                if len(data) < 3:
                    data.append("Open")
            except NoSuchElementException:
                pass
        if len(data) < 3:
            data.append("Closed")
            for i in range(7):
                data.append("N/A")

            return data
        data.append(class_count)
    # Pricing:
    # Memberships
    try:
        memb_options = driver.find_elements(By.CSS_SELECTOR, ".col.col-12.col-lg-4")
        if (len(memb_options) == 0):
            data.append("N/A")
            data.append("N/A")
            data.append("N/A")
        for mtype in memb_options:
            td = mtype.find_element(By.CSS_SELECTOR, ".package-list__price")
            data.append(td.text)
    except NoSuchElementException:
        data.append("N/A")
        data.append("N/A")
        data.append("N/A")
    # Packages
    try:
        cur_button = driver.find_element(By.XPATH,
                                         "//button[contains(@class, 'package-list__type ') and contains(text(), 'Packages')]")
        cur_button.click()
        pack_options = driver.find_elements(By.CSS_SELECTOR, ".col.col-12.col-lg-4")
        for pack in pack_options:
            td = pack.find_element(By.CSS_SELECTOR, ".package-list__price")
            data.append(td.text)
    except NoSuchElementException:
        data.append("N/A")
        data.append("N/A")
        data.append("N/A")

    return data


def cycle_bar():
    data = []
    # Cyclebar
    site_1 = "https://www.cyclebar.com/"

    # Button ID's
    findALocationClass = "super-nav__link"
    locationClass = "location-search-list__card-content"
    showMoreClass = "location-search-list__showMore"

    # Data ID's
    locationsListID = "locations-list"

    # initialize and open
    driver = webdriver.Chrome()
    driver.get(site_1)
    wait = WebDriverWait(driver, 10)
    driver.implicitly_wait(2)
    cur_button = driver.find_element(By.ID, "hs-eu-confirmation-button")
    cur_button.click()

    # move to locations page
    cur_button = driver.find_element(By.CLASS_NAME, findALocationClass)
    cur_button.click()

    # Gather data
    # 1. get all the initial visible locations
    show_more_button = None
    location = 0
    x = True
    while x:
        parent_div = driver.find_element(By.ID, locationsListID)
        child_elements0 = parent_div.find_elements(By.XPATH, "//div[@data-location]")
        child_elements0 = child_elements0[2:]  # cut some junk data
        for element in child_elements0[location:]:
            location += 1
            cur_button = element.find_element(By.XPATH, './/a[contains(text(), "select studio")]')
            link_url = cur_button.get_attribute('href')
            driver.switch_to.new_window('tab')
            driver.get(link_url)
            print(driver.title)
            data.append(get_data_cb(driver))
            print(data[location - 1])
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@data-location]')))
        try:
            show_more_button = driver.find_element(By.CLASS_NAME, 'location-search-list__showMore')
            show_more_button.click()
        except NoSuchElementException:
            x = False
            break
    driver.quit()
    return data


def get_data_cp(driver):
    """[location name, address, status (open, closed, coming soon), # of classes per week]"""
    wait = WebDriverWait(driver, 10)
    data = []
    # Title
    data.append(driver.title.split("|")[0].strip())

    # Address
    driver.execute_script("window.scrollBy(0,1000);")
    address_container = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'location-info-map__info')))
    address_spans = address_container.find_elements(By.XPATH, ".//span[not(contains(@style, 'display:none'))]")
    address_parts = [span.text for span in address_spans]
    data.append(', '.join(address_parts[1:]))

    # Status (open -> at least 1 class this week, coming soon -> indicated on website, closed -> neither)
    # Number of Classes
    try:
        tmp = driver.find_element(By.CLASS_NAME, "location-info-map__details-inner-container")
        tmp.find_element(By.XPATH, ".//span[contains(text(), 'Coming Soon')]")
        data.append("coming soon")
        data.append("N/A")
        return data
    except NoSuchElementException:
        loc_div = driver.find_element(By.ID, "location-scheduler")
        day_list = loc_div.find_element(By.CSS_SELECTOR, ".table.location-scheduler__days")
        day_buttons = day_list.find_elements(By.TAG_NAME, 'button')
        class_count = 0
        for day in day_buttons:
            day.click()
            try:
                scheduler = driver.find_element(By.CSS_SELECTOR, ".table.location-scheduler__list")
                class_count += len(scheduler.find_elements(By.CLASS_NAME, "location-scheduler__class-row"))
                if len(data) < 3:
                    data.append("Open")
            except NoSuchElementException:
                pass
        if len(data) < 3:
            data.append("Closed")
            for i in range(7):
                data.append("N/A")

            return data
        data.append(class_count)
    return data


def club_pilates():
    data = []
    # Cyclebar
    site_1 = "https://www.clubpilates.com/"

    # Button ID's
    findALocationClass = "offer-bar-static__cta"

    # Data ID's
    locationsListID = "locations-list"

    # initialize and open
    driver = webdriver.Chrome()
    driver.get(site_1)
    wait = WebDriverWait(driver, 10)
    driver.implicitly_wait(2)
    cur_button = driver.find_element(By.ID, "hs-eu-confirmation-button")
    cur_button.click()

    # move to locations page
    cur_button = driver.find_element(By.CLASS_NAME, findALocationClass)
    cur_button.click()
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.location-search-list__card'))
    )

    # Gather data
    # 1. get all the initial visible locations
    show_more_button = None
    location = 0
    x = True
    while x:
        parent_div = driver.find_element(By.ID, locationsListID)
        child_elements0 = parent_div.find_elements(By.XPATH, "//div[@data-location]")
        child_elements0 = child_elements0[2:]  # cut some junk data
        for element in child_elements0[location:]:
            location += 1
            cur_button = element.find_element(By.XPATH, './/a[contains(text(), "select studio")]')
            link_url = cur_button.get_attribute('href')
            driver.switch_to.new_window('tab')
            driver.get(link_url)
            print(driver.title)
            data.append(get_data_cp(driver))
            print(data[location - 1])
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@data-location]')))
        try:
            show_more_button = driver.find_element(By.CLASS_NAME, 'location-search-list__showMore')
            show_more_button.click()
        except NoSuchElementException:
            x = False
            break
    driver.quit()
    return data


# Stride fitness is not completed...
def get_data_sf(driver):
    """[location name, address, status (open, closed, coming soon), # of classes per week]"""
    wait = WebDriverWait(driver, 10)
    data = []
    # Title
    data.append(driver.title.split("|")[0].strip())

    # Address
    driver.execute_script("window.scrollBy(0,1000);")
    address_container = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'location-info-map__info')))
    address_spans = address_container.find_elements(By.XPATH, ".//span[not(contains(@style, 'display:none'))]")
    address_parts = [span.text for span in address_spans]
    data.append(', '.join(address_parts[1:]))

    # Status (open -> at least 1 class this week, coming soon -> indicated on website, closed -> neither)
    # Number of Classes
    try:
        tmp = driver.find_element(By.CLASS_NAME, "location-info-map__details-inner-container")
        tmp.find_element(By.XPATH, ".//span[contains(text(), 'Coming Soon')]")
        data.append("coming soon")
        data.append("N/A")
        return data
    except NoSuchElementException:
        loc_div = driver.find_element(By.ID, "location-scheduler")
        day_list = loc_div.find_element(By.CSS_SELECTOR, ".table.location-scheduler__days")
        day_buttons = day_list.find_elements(By.TAG_NAME, 'button')
        class_count = 0
        for day in day_buttons:
            day.click()
            try:
                scheduler = driver.find_element(By.CSS_SELECTOR, ".table.location-scheduler__list")
                class_count += len(scheduler.find_elements(By.CLASS_NAME, "location-scheduler__class-row"))
                if len(data) < 3:
                    data.append("Open")
            except NoSuchElementException:
                pass
        if len(data) < 3:
            data.append("Closed")
            for i in range(7):
                data.append("N/A")

            return data
        data.append(class_count)
    return data


def stride_fitness():
    data = []
    # Cyclebar
    site_1 = "https://www.stridefitness.com/"

    # Button ID's
    findALocationClass = "offer-bar-static__cta"

    # Data ID's
    locationsListID = "locations-list"

    # initialize and open
    driver = webdriver.Chrome()
    driver.get(site_1)
    wait = WebDriverWait(driver, 10)
    driver.implicitly_wait(2)
    driver.quit()
    exit(8)
    cur_button = driver.find_element(By.ID, "hs-eu-confirmation-button")
    cur_button.click()

    # move to locations page
    cur_button = driver.find_element(By.CLASS_NAME, findALocationClass)
    cur_button.click()
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.location-search-list__card'))
    )

    # Gather data
    # 1. get all the initial visible locations
    show_more_button = None
    location = 0
    x = True
    while x:
        parent_div = driver.find_element(By.ID, locationsListID)
        child_elements0 = parent_div.find_elements(By.XPATH, "//div[@data-location]")
        child_elements0 = child_elements0[2:]  # cut some junk data
        for element in child_elements0[location:]:
            location += 1
            cur_button = element.find_element(By.XPATH, './/a[contains(text(), "select studio")]')
            link_url = cur_button.get_attribute('href')
            driver.switch_to.new_window('tab')
            driver.get(link_url)
            print(driver.title)
            data.append(get_data_cp(driver))
            print(data[location - 1])
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@data-location]')))
        try:
            show_more_button = driver.find_element(By.CLASS_NAME, 'location-search-list__showMore')
            show_more_button.click()
        except NoSuchElementException:
            x = False
            break
    driver.quit()
    return data
# end


data_out = club_pilates()
# data_out = stride_fitness()

df = pd.DataFrame(
    columns=['Name', 'Address', 'Status', 'Classes_This_Week'])
for dp in data_out:
    try:
        df = pd.concat([df, pd.DataFrame(({'Name': [dp[0]], 'Address': [dp[1]], 'Status': [dp[2]],
                                           'Classes_This_Week': [dp[3]]}))])
    except IndexError:
        print(dp)

df.to_csv("./Clubpilates.csv", index=False)
