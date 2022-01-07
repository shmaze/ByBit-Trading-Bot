from binance.client import Client
import pandas as pd
import config as cfg
from pybit import HTTP
import joblib

api_key = cfg.API_key
api_secret = cfg.API_secret

model = joblib.load("predictor_model.pkl")


def get_data():
    
    '''
    This function will execute API call to Binance to retrieve data.
    We will export the results of this data into the appropriately named dataframe for further feature engineering.
    '''
    
    client = Client()
    # establishing our blank client
    
    candles = client.get_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_1DAY, limit=90)
    # we only need to request the most recent 90 days to calculate our prediction data
    
    data = pd.DataFrame(candles, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base volume', 'Taker buy quote volume', 'Ignore'])
    # these column labels are as labelled on the Binance API documentation
    
    data.drop(['Close time', 'Ignore'], axis=1, inplace=True)
    # dropping unneeded columns
    
    data['Date'] = data['Date'].apply(lambda x: pd.to_datetime(x, unit='ms'))
    # converting to proper date format for better visual reference
    
    data.set_index('Date', inplace=True)
    # setting index to date
    
    data = data.astype('float64')
    # converting from object type to float type
    
    return data





# we will define a function to run prior to calcualting our averages

def feat_eng(X_df):
    '''
    Intakes "X" portion of data and outputs selected engineered features
    '''
    
    X_df['High/Low'] = X_df['High'] - X_df['Low']
    X_df['volX'] = X_df['Quote asset volume'] / X_df['Volume']
    X_df['quote-buy'] = X_df['Taker buy quote volume'] / X_df['Taker buy base volume']
    
    return X_df





# lets define a function to create our moving averages and incoroprate them into our dataframe

def get_sma(X_df):
    '''
    This function intakes the "X" portion of the data and returns the data with moving average columns applied
    '''
    
    SMAs = [7,30,90]                                                     # 7, 30, and 90 day simple moving averages
    for val in SMAs:
        X_df[str(val)+'sma'] = X_df['Close'].rolling(f'{val}D').mean()   # using the pandas rolling function to calculate mean values over each desired SMA value
        
    return X_df




# Now we want to take the most recent data point possible to make our prediction from

def X_input(X_df):
    x_input = X_df[-1:]        # take the most recent value after calculations for passing into model
    
    return x_input


# now to create a function that ties all of these together and gives us our desired input for the model

def to_predict():
    
    data = get_data()
    data_features = feat_eng(data)
    data_all = get_sma(data_features)
    x_input = X_input(data_all)
    
    return x_input



def get_tp_sl(side):
    '''
    This function will intake whether the trade is a buy (long) or sell (short) position and calculate our stop loss
    and take profit levels for input into trading bot, and output them as a whole integer number.
    '''
    session = HTTP("https://api-testnet.bybit.com")
    result = session.latest_information_for_symbol(
    symbol="BTCUSD")
    price = float(result['result'][0]['index_price'])
    if side == "Buy":
        sl = price - price * 0.0025
        tp = price + price * 0.01
    elif side == "Sell":
        sl = price + price * 0.0025
        tp = price - price * 0.01
    
    return int(tp), int(sl)




to_predict = to_predict()
prediction = model.predict_proba(to_predict)
prediction = prediction[0]

def make_trade(prediction):
    
    if prediction[1] > prediction[0]:
        side = "Buy"
    elif prediction[0] > prediction[1]:
        side = "Sell"
        
    tp, sl = get_tp_sl(side)
    
    session = HTTP("https://api-testnet.bybit.com",
              api_key=api_key,
              api_secret=api_secret)

    order = session.place_active_order(
        symbol="BTCUSD",
        side=side,
        order_type="Market",
        qty=10000,
        time_in_force="GoodTillCancel",
        take_profit=tp,
        stop_loss=sl)
    print(order)
    
    
    
make_trade(prediction)