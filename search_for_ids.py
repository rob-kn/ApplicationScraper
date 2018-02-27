from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementNotVisibleException
import time
import json


def get_ids():
    signature = "https://play.google.com/store/apps/details?id="
    ids_on_page = {}
    elems = driver.find_elements_by_xpath("//a[@href]")
    for elem in elems:
        href = elem.get_attribute("href")
        if href.startswith(signature):
            app_id = href[len(signature):]
            ids_on_page[app_id] = {}
    return ids_on_page


def get_ids_from_search(query):
    query = query.replace(' ', '%20')
    url = "https://play.google.com/store/search?q=" + query + "&c=apps"
    driver.get(url)

    app_ids = {}
    pause = 2
    lastHeight = driver.execute_script("return document.body.scrollHeight")
    while True:
        app_ids.update(get_ids())
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        more_button = driver.find_elements_by_id('show-more-button')
        print(more_button)
        if more_button[0].get_attribute('id') == 'show-more-button':
            try:
                more_button[0].click()
            except ElementNotVisibleException:
                print('element not visible')

        time.sleep(pause)
        newHeight = driver.execute_script("return document.body.scrollHeight")
        if newHeight == lastHeight:
            break
        lastHeight = newHeight
    print("Query '{}' retrieved '{}' apps. They are: {}".format(query, len(app_ids.keys()), app_ids))
    return app_ids


driver = webdriver.Chrome("/Users/rob/PycharmProjects/app_data/chromedriver")

# searches = ["Chat", "Facebook", "Communication", "Social",
#             "Messaging", "Tor", "Private", "Secret",
#             "Encryption", "Spy", "Technical", "Hidden",
#             "Deletion", "Password", "Location", "Money"]
# searches = ["Finance", "Friends", "Contacts", "Talking",
#             "People", "Chatting", "Meet people", "WhatsApp",
#             "Forensic", "Steganography", "Hiding Data", "VPN",
#             "Virtual Private Network", "Networking", "Onion Router", "Texting"]
searches = ["Calls", "Calling", "Networking", "Virtualisation",
            "Mobile", "Telephone", "Electronics", "Chemistry",
            "Proxy", "Religious", "Anonymous", "Anonymity",
            "Privacy", "Account", "Group", "Society"]

for search in searches:
    results = get_ids_from_search(search)

    with open('ids_from_searches.json') as current_ids_json:
        current_ids = json.load(current_ids_json)

    print(len(current_ids.keys()), current_ids)
    current_ids.update(results)
    print(len(current_ids.keys()), current_ids)

    with open('ids_from_searches.json', 'w') as ids_json:
        json.dump(current_ids, ids_json, indent=4)

driver.close()
