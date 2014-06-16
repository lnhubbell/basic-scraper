from scraper import *
import os


def test_write_read():

    to_write = "this is a bunch of test data"
    write_to_file('test.html', to_write)
    html, encoding = read_from_file('test.html')
    print html
    os.remove('test.html')
    assert html is not None
    assert html == "this is a bunch of test data"


def test_parse():
    afile = read_from_file('apartments.html')
    parsed = parse_source(afile)
    assert parsed.find()
