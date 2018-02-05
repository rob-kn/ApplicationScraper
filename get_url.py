from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from random import randint


def simple_get(url, use_proxies=True):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None
    """
    if use_proxies:
        proxy_num = randint(0, 11)
        with open('fast_proxies.txt') as prox:
            for indx, line in enumerate(prox):
                if indx == proxy_num:
                    fields = line.split('\t')
                    https_proxy = "https://{}:{}".format(fields[0].strip(), fields[1].strip())
                    print("Getting '{}' using proxy '{}:{}'".format(url, fields[0].strip(), fields[1].strip()))
        proxy_dict = {
            "https": https_proxy
        }
    else:
        proxy_dict = {}
    try:
        with closing(get(url, stream=True, timeout=10, proxies=proxy_dict)) as resp:
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