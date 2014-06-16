import requests
import sys
from bs4 import BeautifulSoup


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
    return read_from_file('apartments.html')

# write_to_file('apartments.html', fetch_search_results("", 300)[0])


def parse_source(html, the_encoding='utf-8'):
    parsed = BeautifulSoup(html, from_encoding=the_encoding)
    return parsed


def extract_listings(parsed):
    # location_attrs = {'data-latitude': True, 'data-longitude': True}
    listings = parsed.find_all('p', class_='row')  # , attrs=location_attrs)
    extracted = []
    for listing in listings:
        link = listing.find('span', class_='pl').find('a')
        price_span = listing.find('span', class_='price')
        this_listing = {
            'link': link.attrs['href'],
            'description': link.string.strip(),
            'price': price_span.string.strip(),
            'size': price_span.next_sibling.strip(' \n-/')
        }
        extracted.append(this_listing)
    return extracted







if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        html, encoding = read_search_results()
    else:
        html, encoding = fetch_search_results(
            minAsk=5#, maxAsk=10000
        )
    print encoding
    doc = parse_source(html, encoding)
    listings = extract_listings(doc)
    print len(listings)
    print listings[5]
