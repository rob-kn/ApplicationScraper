from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from pprint import pprint
from multiprocessing.pool import ThreadPool
from time import time as timer
import json


def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns true if the response seems to be HTML, false otherwise
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors.
    This function just prints them, but you can
    make it do anything.
    """
    print(e)


def get_app_categories(raw_html):
    categories = []
    html = BeautifulSoup(raw_html, 'html.parser')
    for a in html.select('a'):
        # Ignore 'Games' and 'Family' section of dropdown
        if a['href'].startswith("/store/apps/category/") and \
                not a['href'].startswith("/store/apps/category/GAME") and \
                not a['href'].startswith("/store/apps/category/FAMILY"):
            categories.append(a['href'])
    return categories


def get_sub_categorys(url):
    sub_categories = {}
    raw_html = simple_get(url)
    html = BeautifulSoup(raw_html, 'html.parser')
    data = html.findAll('h2')
    for h2 in data:
        for a in h2.select('a'):
            name = a.text.strip()
            url = a['href']
            if name != "See more" and name != "Recommended for you":
                sub_categories[name] = url
    # pprint(sub_categories)
    return sub_categories


def get_apps_on_page(url):
    app_ids = set()
    raw_html = simple_get(url)
    soup = BeautifulSoup(raw_html, 'html.parser')
    for a in soup.select('a'):
        signature = "/store/apps/details?id="
        if a['href'].startswith(signature):
            app_id = a['href'][len(signature):]
            app_ids.add(app_id)
    return app_ids


def get_app_details(app_id):
    details = {}
    app_page_url = "https://play.google.com/store/apps/details?id=" + app_id
    raw_html = simple_get(app_page_url)
    if not raw_html:
        return app_id, None
    soup = BeautifulSoup(raw_html, 'html.parser')
    title = soup.find("div", {"class": "id-app-title"}).text
    details['title'] = title.strip()
    genre = soup.find("span", {"itemprop": "genre"}).text
    details['genre'] = genre.strip()
    desc = soup.find("div", {"itemprop": "description"}).text
    desc = desc.replace('<br>', '\n')
    details['description'] = desc.strip()

    meta_info = soup.findAll("div", {"class": "meta-info"})
    for info in meta_info:
        info_title = info.find("div", {"class": "title"}).text
        info_content = info.find(attrs={"class": "content"}).text
        details[info_title.strip()] = info_content.strip()

    pprint(details)

    return app_id, details


def get_many_app_details(app_ids):

    start = timer()
    results = ThreadPool(20).imap_unordered(get_app_details, app_ids)
    app_dict = {}
    for result in results:
        app_dict[result[0]] = result[1]

    with open('apps.json') as app_json:
        current_apps = json.load(app_json)
        print(current_apps)

    current_apps.update(app_dict)

    with open('apps.json', 'w') as app_json:
        json.dump(current_apps, app_json, indent=4)

    print("Elapsed Time: %s" % (timer() - start,))


def get_app_ids(max_count):
    with open('apps.json') as apps_json:
        json_content = json.load(apps_json)
    with open('app_ids.txt') as ids_file:
        app_ids = [app_id.strip() for app_id in ids_file if app_id.strip()]
    new_ids = []
    for app_id in app_ids:
        if app_id not in json_content:
            print('App id not in current json.')
            new_ids.append(app_id)
        else:
            if not json_content[app_id]:
                print('App id contains no information.')
                new_ids.append(app_id)
        if len(new_ids) == max_count:
            break
    return new_ids


if __name__ == "__main__":
    main_page_url = "https://play.google.com"

    # get main categories
    # app_store_page = main_page_url + "/store/apps"
    # raw_html = simple_get(app_store_page)
    # categories = get_app_categories(raw_html)
    # pprint(categories)

    # get sub categories
    # url = "https://play.google.com/store/apps/category/COMMUNICATION"
    # sub_cats = get_sub_categorys(url)

    # get all app ids from page
    # url = "https://play.google.com/store/apps/collection/promotion_cp_messaging_apps?clp=SjIKIQobcHJvbW90aW9uX2NwX21lc3NhZ2luZ19hcHBzEAcYAxINQ09NTVVOSUNBVElPTg%3D%3D:S:ANO1ljIyLhU"
    # print(get_apps_on_page(url))

    # whatsapp test
    # whatsapp_id = "com.whatsapp"
    # app_id, details = get_app_details(whatsapp_id)

    # get app ids from multiple pages
    # all_app_ids = set()
    # for category in categories:
    #     c_url = main_page_url + category
    #     sub_categories = get_sub_categorys(c_url)
    #     for name, sub_category_path in sub_categories.items():
    #         print("Trying '{}' page at path '{}'".format(name, sub_category_path))
    #         sc_url = main_page_url + sub_category_path
    #         app_ids_on_page = get_apps_on_page(sc_url)
    #         all_app_ids = all_app_ids.union(app_ids_on_page)
    #
    # with open('app_ids.txt', 'w') as f:
    #     for app_id in all_app_ids:
    #         f.write(app_id + '\n')

    # get multiple app info
    app_ids = get_app_ids(5)
    get_many_app_details(app_ids)
