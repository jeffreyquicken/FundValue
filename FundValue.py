#  IMPORTS
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import json
import datetime
import random
import collections
from rich import print
from rich import box
from rich.table import Table
from rich.progress import track


def readUrls():
    with open("ISIN.txt") as f:
        lines = f.read().splitlines()
        return lines

fundsUrl = [
  "http://www.morningstar.be/be/funds/snapshot/snapshot.aspx?id=F0000043PR",
  "http://www.morningstar.be/be/funds/snapshot/snapshot.aspx?id=F00000T4KE",
  "http://www.morningstar.be/be/funds/snapshot/snapshot.aspx?id=F0GBR067EX",
  "http://www.morningstar.be/be/funds/snapshot/snapshot.aspx?id=F000010L39"
]


data = collections.OrderedDict()


def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
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
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    """
    Prints the error.
    """
    print(e)

#MORNINGSTAR
# def get_value(url='http://www.morningstar.be/be/funds/snapshot/snapshot.aspx?id=f00000t4ke', debug=False):
#     """
#     Downloads the page where the fund value is located
#     and returns the NIV.
#     """
#     response = simple_get(url)
#     if response is not None:
#
#         html = BeautifulSoup(response, 'html.parser')
#
#         table = html.find('table', attrs={'snapshotTextColor snapshotTextFontStyle snapshotTable overviewKeyStatsTable'})
#         trs = table.findAll('tr')
#         td = trs[1].find('td', attrs={'line text'})
#         text = td.getText()
#         string = text.replace('EUR', '')
#         esc = string.replace('\u00a0', '')
#         value = float(esc.replace(',', '.'))
#
#         if debug is True:
#             print(td)
#             print(value)
#
#         return value
#
#     raise Exception('Error retrieving contents at {}'.format(url))


#Financial Times
def get_value(url='https://markets.ft.com/data/funds/tearsheet/summary?s=LU1670724373:EUR', debug=False):
    """
    Downloads the page where the fund value is located
    and returns the NIV.
    """
    response = simple_get(url)

    if response is not None:
        html = BeautifulSoup(response, 'html.parser')

        ul = html.find('ul', attrs={'mod-tearsheet-overview__quote__bar'})

        li = ul.findAll('li')

        el = li[0]

        span = el.find('span', attrs={'mod-ui-data-list__value'})

        niv = span.getText()
        value = niv.replace('.', ',')

        if debug is True:
            print(ul)
            print("\n")
            print(li)
            print("\n")
            print(el)
            print("\n")
            print(span)
            print("\n")
            print(niv)

        return value

    raise Exception('Error retrieving contents at {}'.format(url))

#MORNINGSTAR
# def get_name(url='http://www.morningstar.be/be/funds/snapshot/snapshot.aspx?id=f00000t4ke', debug=False):
#     """
#         Downloads the page where the fund is located
#         and returns the name.
#         """
#     response = simple_get(url)
#
#     if response is not None:
#
#         html = BeautifulSoup(response, 'html.parser')
#
#         table2 = html.find('table', attrs={'snapshotTextColor snapshotTextFontStyle snapshotTitleTable'})
#         trs2 = table2.findAll('tr')
#         td2 = trs2[0].find('td')
#         div = td2.find('div', attrs={'snapshotTitleBox'})
#         h1 = div.find('h1')
#         name = h1.getText()
#
#         if debug is True:
#             print(name)
#
#         return name
#
#     raise Exception('Error retrieving contents at {}'.format(url))

#FINANCIAL TIMES
def get_name(url='https://markets.ft.com/data/funds/tearsheet/summary?s=LU1670724373:EUR', debug=False):
    """
        Downloads the page where the fund is located
        and returns the name.
        """
    response = simple_get(url)

    if response is not None:

        html = BeautifulSoup(response, 'html.parser')

        h1 = html.find('h1', attrs={'mod-tearsheet-overview__header__name mod-tearsheet-overview__header__name--large'})
        name = h1.getText()

        if debug is True:
            print(name)

        return name

    raise Exception('Error retrieving contents at {}'.format(url))


def create_dict():
    """
    Returns a dictionary with key:value = fund name:value for each fund in fundsUrl
    """
    dat = {}
    for j in range(0, len(fundsUrl)):
        dat[get_name(fundsUrl[j])] = get_value(fundsUrl[j])

    return dat


def add_dict(result, to_add, test=False):
    """
    Adds a dictionary to another dictionary as with the date as key and the dictionary as value.
    :param result: dictionary to be added to
    :param to_add: dictionary to add to result
    :param test: boolean used to set key for to_add in result ta a random integer
    :return:
    """
    if test is True:
        date = random.randint(0,50)
    else:
        temp = datetime.datetime.now()
        date = temp.strftime('%m/%d/%Y')
    result[date] = to_add


def update_json():
    """
    Updates the data.json file.
    """

    with open('data.json', 'r') as f:
        read = json.load(f)
    add_dict(read, create_dict(), True)

    with open("data.json", "w") as jsonFile:
        json.dump(read, jsonFile, default=str)

# def get_all_values():
#     for i in readUrls():
#         name = get_name(i)
#         value = str(get_value(i))
#         print(name + ": " + value)
#     temp = datetime.datetime.now()
#     date = temp.strftime('%m/%d/%Y')
#     table = Table(title="Fund values - " + date)
#     table.add_column("Fund Name", justify="right", style="cyan", no_wrap=True)
#     table.add_column("Value", style="magenta")
#     table.add_row(name, value)

def get_all_values():
    temp = datetime.datetime.now()
    date = temp.strftime('%d/%m/%Y')
    table = Table(title="Fund values - " + date, box=box.ROUNDED)
    table.add_column("Fund Name", justify="left", style="cyan")
    table.add_column("Value", justify="left", style="bright_white")
    for i in track(readUrls(), description="Retrieving..."):
        name = get_name(i)
        value = str(get_value(i))
        table.add_row(name, value)
    print(table)


def main():
    #update_json()
    #readUrls()
    #get_value()
    get_all_values()


main()


