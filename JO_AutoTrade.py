import time
import pyupbit
import datetime
import numpy as np

access = "3tFtNvy2cpHYAzLqbRJxTxrLjtxuSJcbcqWrFJz8"
secret = "yxFwGIBn3i5vMltclXyhnvxxYx8WHV8FLIbep6b9"

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# Best k를 구하기
def get_ror(k=0.5):
    df = pyupbit.get_ohlcv("KRW-BTC", interval='day', count=14)
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)

    fee = 0.05
    df['ror'] = np.where(df['high'] > df['target'],
                         df['close'] / df['target'] - fee,
                         1)

    ror = df['ror'].cumprod()[-2]
    return ror
def get_BestK():
    bestK = 0
    ror = 0
    for k in np.arange(0.1, 1.0, 0.1):
        tmp = get_ror(k)
        if ror < tmp:
            ror = tmp
            bestK = k
    return bestK

isBuy = False

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-BTC", get_BestK())
            current_price = get_current_price("KRW-BTC")
            if isBuy == False:
                if target_price < current_price:
                    krw = round(get_balance("KRW") / 5)
                    if krw > 5000:
                        upbit.buy_market_order("KRW-BTC", krw*0.9995)
        else:
            if isBuy == True:
                btc = get_balance("KRW-BTC")
                if btc * pyupbit.get_current_price("KRW-BTC") > 5000:
                    upbit.sell_market_order("KRW-BTC", btc*0.9995)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
