from bs4 import BeautifulSoup
from pprint import pprint
from get_url import simple_get


def get_app_categories(raw_html):
    categories = []
    html = BeautifulSoup(raw_html, 'html.parser')
    for a in html.select('a'):
        # Ignore 'Games' and 'Family' section of dropdown
        # if a['href'].startswith("/store/apps/category/") and \
        #         not a['href'].startswith("/store/apps/category/GAME") and \
        #         not a['href'].startswith("/store/apps/category/FAMILY"):
        #     categories.append(a['href'])

        # Only 'Games' and 'Family' section of dropdown
        if a['href'].startswith("/store/apps/category/GAME") or \
                a['href'].startswith("/store/apps/category/FAMILY"):
            categories.append(a['href'])
    return categories


def get_sub_categorys(url):
    sub_categories = {}
    raw_html = simple_get(url, use_proxies=False)
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
    raw_html = simple_get(url, use_proxies=False)
    soup = BeautifulSoup(raw_html, 'html.parser')
    for a in soup.select('a'):
        signature = "/store/apps/details?id="
        if a['href'].startswith(signature):
            app_id = a['href'][len(signature):]
            app_ids.add(app_id)
    return app_ids


if __name__ == "__main__":
    main_page_url = "https://play.google.com"

    # get main categories
    app_store_page = main_page_url + "/store/apps"
    raw_html = simple_get(app_store_page, use_proxies=False)
    categories = get_app_categories(raw_html)
    pprint(categories)

    # get sub categories (test)
    # url = "https://play.google.com/store/apps/category/COMMUNICATION"
    # sub_cats = get_sub_categorys(url)

    # get all app ids from page (test)
    # url = "https://play.google.com/store/apps/collection/promotion_cp_messaging_apps?clp=SjIKIQobcHJvbW90aW9uX2NwX21lc3NhZ2luZ19hcHBzEAcYAxINQ09NTVVOSUNBVElPTg%3D%3D:S:ANO1ljIyLhU"
    # print(get_apps_on_page(url))

    # get app ids from multiple pages
    all_app_ids = set()
    for category in categories:
        c_url = main_page_url + category
        sub_categories = get_sub_categorys(c_url)
        for name, sub_category_path in sub_categories.items():
            print("Trying '{}' page at path '{}'".format(name, sub_category_path))
            sc_url = main_page_url + sub_category_path
            app_ids_on_page = get_apps_on_page(sc_url)
            all_app_ids = all_app_ids.union(app_ids_on_page)

    with open('app_ids_games_and_family.txt', 'w') as f:
        for indx, app_id in enumerate(all_app_ids):
            if indx == 0:
                f.write(app_id)
            else:
                f.write("\n" + app_id)
