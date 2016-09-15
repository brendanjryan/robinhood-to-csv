import csv
import json
import urllib

import requests


class RobinhoodClient(object):
  """

  """
  API_ROOT = "https://api.robinhood.com/"

  URI = {
    "AUTH": API_ROOT + "api-token-auth/",
    "ORDER": API_ROOT + "orders/",
    "INSTRUMENT": API_ROOT + "instruments/"
  }

  API_HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en;q=1, fr;q=0.9, de;q=0.8, ja;q=0.7, nl;q=0.6, it;q=0.5",
    "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
    "X-Robinhood-API-Version": "1.0.0",
    "Connection": "keep-alive",
    "User-Agent": "Robinhood/823 (iPhone; iOS 7.1.2; Scale/2.00)"
  }

  def __init__(self, username, password):
    self.session = requests.session()
    self.session.proxies = urllib.getproxies()
    self.session.headers = RobinhoodClient.API_HEADERS
    self.username = username
    self.password = password
    self.orders = []
    self.auth_token = None

    self.login()


  def login(self):
    qs = "password=%s&username=%s" % (self.password, self.username)
    res = self.session.post(self.URI['AUTH'], data=qs).json()

    self.auth_token = res['token']
    self.API_HEADERS['Authorization'] = 'Token {}'.format(self.auth_token)

  def get_ticker_symbol(self, order):
    instrument = order['instrument']
    instrument = self.session.get(instrument).json()
    return instrument['symbol']

  def get_orders(self):

    def _page(uri, orders=None):
      if not orders:
        orders = []
        
      res = self.session.get(uri).json()
      orders += res['results']

      if res['next']:
        return _page(res['next'])

      self.orders = orders
      return orders

    return _page(self.URI["ORDER"])


class RobinhoodExporter(RobinhoodClient):

  DESIRED_KEYS = ['average_price', 'quantity', 'side', 'created_at']

  def __init__(self, username, password, filename="robinhood.csv"):
    super(RobinhoodExporter, self).__init__(username, password)
    self.filename = filename


  def format_orders(self, orders):
    """Pull out price, quantity, ticker symbol, date, and action (BUY,SELL) only if filled
    """

    stripped_history = []

    for item in orders:
      if item['state'] and item['state'] == 'filled':
        stripped_item = { key: item[key] for key in self.DESIRED_KEYS }
        stripped_item['symbol'] = self.get_ticker_symbol(item)
        stripped_history.append(stripped_item)

    return stripped_history


  def _dump_csv(self, orders):
    with open(self.filename, 'wb') as f:
      w = csv.DictWriter(f, orders[0].keys())
      w.writeheader()
      w.writerows(orders)


  def to_csv(self):
    orders = self.get_orders()
    orders = self.format_orders(orders)
    self._dump_csv(orders)


