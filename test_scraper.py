from scraper import *

def test_write_read():
    to_write = fetch_search_results(minAsk=200)
    write_to_file('test.html', to_write)
    html, encoding = read_from_file('test.html')
    assert html is not None
