from chalice import Chalice
import requests, json
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from API_PASSWORDS import API_KEY, API_PASS

app = Chalice(app_name='aws-lambda-1')
api_key = API_KEY
api_secret = API_PASS
BASE_URL = "https://paper-api.alpaca.markets"
ORDERS_URL = "{}/v2/orders".format(BASE_URL)
HEADERS = {'APCA-API-KEY-ID': api_key, 'APCA-API-SECRET-KEY': api_secret}


@app.route('/buystock', methods=['POST'])

def calculate_atr(data, period=14):
    high_low = data['High'] - data['Low']
    high_close = abs(data['High'] - data['Close'].shift())
    low_close = abs(data['Low'] - data['Close'].shift())

    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = true_range.rolling(window=period).mean()
    return atr


def buystock():
    # This is the JSON body the user sent in their POST request.
    request = app.current_request
    webhook_message = request.json_body

    end_date = datetime.now()
    start_date = end_date - timedelta(days=14)

    stock_data = yf.download(webhook_message['ticker'], start=start_date, end=end_date, interval='5m')

    atr = calculate_atr(stock_data)
    if atr >= 150:
        data = {
            "symbol": webhook_message['ticker'],
            "qty": round(5000 / webhook_message['close']),
            "side": "buy",
            "type": "limit",
            "limit_price": round(webhook_message['close'], 2),
            "time_in_force": "cls",
            "order_class": "bracket",
            "take_profit": {
                "limit_price": round(webhook_message['close'] * 1.10, 2)
            },
            "stop_loss": {
                "stop_price": round(webhook_message['close'] * 0.97, 2),
            }
        }

        r = requests.post(ORDERS_URL, json=data, headers=HEADERS)

        response = json.loads(r.content)

        print(response)
        print(response.keys())

        return {
            'Message': 'I bought the stock',
            'Webhook Message': webhook_message
        }

# The view function above will return {"hello": "world"}
# whenever you make an HTTP GET request to '/'.
#
# Here are a few more examples:
#
# @app.route('/hello/{name}')
# def hello_name(name):
#    # '/hello/james' -> {"hello": "james"}
#    return {'hello': name}
#
# @app.route('/users', methods=['POST'])
# def create_user():
#     # This is the JSON body the user sent in their POST request.
#     user_as_json = app.current_request.json_body
#     # We'll echo the json body back to the user in a 'user' key.
#     return {'user': user_as_json}
#
# See the README documentation for more examples.
#
