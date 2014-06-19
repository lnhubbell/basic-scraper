import requests
import sys
from bs4 import BeautifulSoup
import json


def fetch_search_results(
    query=None, minAsk=None, maxAsk=None, bedrooms=None
):
    search_params = {
        key: val for key, val in locals().items() if val is not None
    }
    if not search_params:
        raise ValueError("No valid keywords")

    base = 'http://seattle.craigslist.org/search/apa'
    resp = requests.get(base, params=search_params, timeout=3)
    resp.raise_for_status()  # <- no-op if status==200
    return resp.content, resp.encoding


def write_to_file(the_file, to_write):
    with open(the_file, 'w') as outfile:
        outfile.write(to_write)


def read_from_file(the_file):
    with open(the_file, 'r') as outfile:
        return outfile.read(), "utf-8"


def read_search_results():
    with open('apartments.html', 'r') as outfile:
        return outfile.read(), "utf-8"


def fetch_json_results(**kwargs):
    base = 'http://seattle.craigslist.org/jsonsearch/apa'
    resp = requests.get(base, params=kwargs)
    resp.raise_for_status()
    return resp.json()


def fetch_json_results_for_write(**kwargs):
    base = 'http://seattle.craigslist.org/jsonsearch/apa'
    resp = requests.get(base, params=kwargs)
    resp.raise_for_status()
    return resp.content


def parse_source(html, the_encoding='utf-8'):
    parsed = BeautifulSoup(html, from_encoding=the_encoding)
    return parsed


def extract_listings(parsed):
    # location_attrs = {'data-latitude': True, 'data-longitude': True}
    listings = parsed.find_all('p', class_='row')
    # delete the line where you create a list in which to store
    # your listings
    for listing in listings:
        # location = {key: listing.attrs.get(key, '') for key in location_attrs}
        link = listing.find('span', class_='pl').find('a')
        price_span = listing.find('span', class_='price')
        this_listing = {
            # 'location': location,
            'pid': listing.attrs.get('data-pid', ''),
            'link': link.attrs['href'],
            'description': link.string.strip(),
            'price': price_span.string.strip(),
            'size': price_span.next_sibling.strip(' \n-/')
        }
        # delete the line where you append this result to a list
        yield this_listing  # This is the only change you need to make


def add_location(listing, search):
    """True if listing can be located, False if not"""
    if listing['pid'] in search:
        match = search[listing['pid']]
        listing['location'] = {
            'data-latitude': match.get('Latitude', ''),
            'data-longitude': match.get('Longitude', ''),
        }
        return True
    return False


def add_address(listing):
    api_url = 'http://maps.googleapis.com/maps/api/geocode/json'
    loc = listing['location']
    latlng_tmpl = "{data-latitude},{data-longitude}"
    parameters = {
        'sensor': 'false',
        'latlng': latlng_tmpl.format(**loc),
    }
    resp = requests.get(api_url, params=parameters)
    resp.raise_for_status()  # <- this is a no-op if all is well
    data = resp.json()
    if data['status'] == 'OK':
        best = data['results'][0]
        listing['address'] = best['formatted_address']
    else:
        listing['address'] = 'unavailable'
    return listing


if __name__ == '__main__':
    import pprint
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        html, encoding = read_search_results()
    else:
        html, encoding = fetch_search_results(
            minAsk=500, maxAsk=1000, bedrooms=2
        )
    doc = parse_source(html, encoding)
    # print doc
    json_res = fetch_json_results(minAsk=500, maxAsk=1000, bedrooms=2)
    search = {j['PostingID']:j for j in json_res[0]}
    for listing in extract_listings(doc):
        if (add_location(listing, search)):
            listing = add_address(listing)
            pprint.pprint(listing)
        else:
            pass# print "add location failed"


# if __name__ == '__main__':
#     write_to_file('apartments.html', fetch_search_results(minAsk=500, maxAsk=1000, bedrooms=2))
