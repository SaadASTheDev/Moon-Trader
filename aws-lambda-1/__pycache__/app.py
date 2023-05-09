from chalice import Chalice
import requests, json



app = Chalice(app_name='aws-lambda-1')
api_key = "PKM0LTQM0LRG3BWEDDDA"
api_secret = "EtWdtrvzM1oOaJuK8qoYh2cM76XC45v3QH06jMKV"
BASE_URL = "https://paper-api.alpaca.markets"
ORDERS_URL = "{}/v2/orders".format(BASE_URL)
HEADERS = {'APCA-API-KEY-ID': api_key, 'APCA-API-SECRET-KEY': api_secret}

@app.route('/buystock', methods=['POST'])
def buystock():
    # This is the JSON body the user sent in their POST request.
    request = app.current_request
    webhook_message = request.json_body

    data = {
            "symbol": webhook_message['ticker'],
            "qty": 100,
            "side": "buy",

            "type": "limit",
            "limit_price": round(webhook_message['close'],2),
            "time_in_force": "gtc",
            "order_class": "bracket",
            "take_profit": {
                "limit_price": round(webhook_message['close'] * 1.01 ,2) 
            },
            "stop_loss": {
                "stop_price": round(webhook_message['close'] * 0.91,2)
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
