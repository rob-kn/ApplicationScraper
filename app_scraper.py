from bs4 import BeautifulSoup
from pprint import pprint
from multiprocessing.pool import ThreadPool
from time import time as timer
import json
from get_url import simple_get


def get_app_details(app_id):
    # print("Getting details for app with id '{}'".format(app_id))
    details = {}
    app_page_url = "https://play.google.com/store/apps/details?id=" + app_id + "&hl=en_GB"
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
    score = soup.find("div", {"class": "score"})
    details['score'] = score.text.strip() if score else None

    meta_info = soup.findAll("div", {"class": "meta-info"})
    for info in meta_info:
        info_title = info.find("div", {"class": "title"}).text
        info_content = info.find(attrs={"class": "content"}).text
        details[info_title.strip()] = info_content.strip()

    # pprint(details)
    print("App details retrieved for app with id '{}'".format(app_id))

    return app_id, details


def get_many_app_details(app_ids):
    print("Getting app details for {}.".format(', '.join(app_ids)))
    start = timer()
    results = ThreadPool(20).imap_unordered(get_app_details, app_ids)
    app_dict = {}
    for result in results:
        app_dict[result[0]] = result[1]

    with open('apps.json') as app_json:
        current_apps = json.load(app_json)

    current_apps.update(app_dict)

    with open('apps.json', 'w') as app_json:
        json.dump(current_apps, app_json, indent=4)

    print("Elapsed Time: %s" % (timer() - start,))


def get_app_ids(max_count):
    print("Retrieving a maximun of {} app_ids".format(max_count))
    with open('apps.json') as apps_json:
        json_content = json.load(apps_json)
    new_ids = []
    for app_id in json_content.keys():
        if not json_content[app_id]:
            new_ids.append(app_id)
            print("App id '{}' contains no information in current json and has been returned.".format(app_id))
        if len(new_ids) == max_count:
            break
    return new_ids


if __name__ == "__main__":
    # get multiple app info
    for i in range(3):
        app_ids = get_app_ids(400)
        get_many_app_details(app_ids)

    with open('apps.json') as a:
        apps = json.load(a)
        detailed = 0
        for pkg in apps.keys():
            if apps[pkg]:
                detailed += 1
    print("JSON contains {} packages, {} with information.".format(len(apps.keys()), detailed))

