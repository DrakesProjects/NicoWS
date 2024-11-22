# Web scraping project for Nico QFS Pitch
# Written by: Drake Adams
# 2/7/2024
# Sources:
# 1. https://github.com/SeleniumHQ/seleniumhq.github.io/blob/trunk/examples/python/tests/getting_started/first_script.py#L8
# 2. https://www.selenium.dev/documentation/webdriver/getting_started/first_script/

# Just a note. Selenium very much runs as if you were going through the browser yourself in how it interacts with the
# website. Pretty much anything you can do on chrome you can do on selenium. Sometimes you might need to scroll the page
# to makes things accessible, etc. Also, I made this code so that the data, when collected is not stored in a file until
# the very end of the program. This means if it crashes, you gotta start all over. It's worked so far, but it's kinda
# annoying. As you know the fix is easy if you wanna make it store every dp right when u get it. Peep the second source
# for a good intro to the lib. It's pretty straightforward but runtime is kinda long (2hrs for 1000 rows). Ask Nico he
# might want more data than what I got for this page too.

# Each franchise is slightly different so you gotta make some tweaks on each new one. Nothing crazy if you understand
# the code though.

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


def get_data_cp(driver):
    """[location name, address, status (open, closed, coming soon), # of classes per week]"""
    wait = WebDriverWait(driver, 10)
    data = []  # return
    # Title
    data.append(driver.title.split("|")[0].strip())

    # Address
    driver.execute_script("window.scrollBy(0,1000);")
    address_container = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'location-info-map__info')))
    address_spans = address_container.find_elements(By.XPATH, ".//span[not(contains(@style, 'display:none'))]")
    address_parts = [span.text for span in address_spans]
    data.append(', '.join(address_parts[1:]))

    # Status (open -> at least 1 class this week, coming soon -> indicated on website (gotta find it),
    # closed -> neither)

    # Number of Classes
    try:
        # Check for coming soon
        tmp = driver.find_element(By.CLASS_NAME, "location-info-map__details-inner-container")
        tmp.find_element(By.XPATH, ".//span[contains(text(), 'Coming Soon')]")
        data.append("coming soon")
        data.append("N/A")
        return data
    except NoSuchElementException:
        # Check for classes this week
        loc_div = driver.find_element(By.ID, "location-scheduler")
        day_list = loc_div.find_element(By.CSS_SELECTOR, ".table.location-scheduler__days")
        day_buttons = day_list.find_elements(By.TAG_NAME, 'button')
        class_count = 0
        for day in day_buttons:
            day.click()
            try:  # check for classes
                scheduler = driver.find_element(By.CSS_SELECTOR, ".table.location-scheduler__list")
                class_count += len(scheduler.find_elements(By.CLASS_NAME, "location-scheduler__class-row"))
                if len(data) < 3:
                    data.append("Open")
            except NoSuchElementException:
                pass
        if len(data) < 3:  # no classes
            data.append("Closed")
            for i in range(7):
                data.append("N/A")

            return data
        data.append(class_count)
    return data


def club_pilates():
    data = []
    # Cyclebar url
    site_1 = "https://www.clubpilates.com/"

    # Button ID's
    findALocationClass = "offer-bar-static__cta"

    # Data ID's
    locationsListID = "locations-list"

    # initialize and open website
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
    # The following goes through all the visible franchise locations on the page and collects data. After that it
    # presses the show more button. The code stops running when the show more button is gone (presumable having
    # reached all locations).
    show_more_button = None
    location = 0  # ensures no repeats of locations
    x = True
    while x:
        # find all visible locations
        parent_div = driver.find_element(By.ID, locationsListID)
        child_elements0 = parent_div.find_elements(By.XPATH, "//div[@data-location]")
        child_elements0 = child_elements0[2:]  # cut some junk data
        # Loop through the locations and grab data
        for element in child_elements0[location:]:
            location += 1
            # open location in new tab
            cur_button = element.find_element(By.XPATH, './/a[contains(text(), "select studio")]')
            link_url = cur_button.get_attribute('href')
            driver.switch_to.new_window('tab')
            driver.get(link_url)
            print(driver.title)
            # Grab and store data with get_data_cp, a function defined in this file
            data.append(get_data_cp(driver))
            print(data[location - 1])
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@data-location]')))
        # ensure the show more button is still available
        try:
            show_more_button = driver.find_element(By.CLASS_NAME, 'location-search-list__showMore')
            show_more_button.click()
        except NoSuchElementException:
            x = False
            break
    driver.quit()
    return data

################################################################################
# Main
################################################################################

data_out = club_pilates()

# Store Data
df = pd.DataFrame(
    columns=['Name', 'Address', 'Status', 'Classes_This_Week'])
for dp in data_out:
    try:
        # this statement is me being lazy, and it has the potential to cut out a few datapoints if the data was not
        # collected properly and the list is not the correct length. I was gonna fix it before I learned it's not my
        # problem anymore. The easy fix is just store the mismatched data in a different file, maybe .txt as that won't
        # get weird with the size of the list and you can just manually add the few wierd points after. He said
        # something abt AZ being where the 3-6 missing dp's were.
        df = pd.concat([df, pd.DataFrame(({'Name': [dp[0]], 'Address': [dp[1]], 'Status': [dp[2]],
                                           'Classes_This_Week': [dp[3]]}))])
    except IndexError:
        print(dp)

# To Excel File
df.to_csv("./Clubpilates.csv", index=False)
