from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
from crypto_portfolio import db
from crypto_portfolio.models import Coins

import os
from dotenv import load_dotenv

load_dotenv()

url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
parameters = {
    'start': '1',
    'limit': '50',
    'convert': 'USD'
}
headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': os.getenv('APIKEY'),
}

session = Session()
session.headers.update(headers)

try:
    response = session.get(url, params=parameters)
    json_data = json.loads(response.text)
    for coin in json_data['data']:
        name = coin['name']
        symbol = coin['symbol']
        current_price = coin['quote']['USD']['price']

        coin = Coins.query.filter_by(name=name).first()
        if coin:
            coin.current_price = current_price
        else:
            coin = Coins(name=name, symbol=symbol, current_price=current_price)
            db.session.add(coin)
        db.session.commit()
except (ConnectionError, Timeout, TooManyRedirects) as e:
    print(e)
