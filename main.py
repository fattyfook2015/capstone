import pandas as pd

import datetime as dt

import utils.Config as cfg

import utils.AlphaVantageUtils as av
import utils.PostgresUtils as pg
import utils.PriceUpdater as pu
import utils.FeaturesUpdater as fu

_VERSION_NO = '1.1'

_LBL_FUNCTION = 'function'
_LBL_PARAMETERS = 'parameters'

_VAL_GET_PRICES = 'get_prices'
_VAL_GET_PRICES_WITH_FEATURES = 'get_prices_features'
_VAL_UPDATE_PRICES = 'update_prices'

_VAL_GET_FEATURES = 'get_features'
_VAL_UPDATE_FEATURES = 'update_features'

_VAL_GET_ALL_SYMBOLS = 'get_all_symbols'
_VAL_GET_SYMBOL = 'get_symbol'

_PARAM_FUNC = 'func'
_PARAM_TICKER = 'ticker'
_PARAM_INTERVAL = 'interval'
_PARAM_SIZE = 'size'
_PARAM_DATETIME = 'datetime'
_PARAM_LIMIT = 'limit'
_PARAM_START = 'start'
_PARAM_END = 'end'


def get_all_symbols():

    symbols = pg.get_symbols()

    if symbols is None:
        return 'No symbols found!'
    else:
        df = pd.DataFrame(symbols, columns=[pg._COL_NAME, pg._COL_TICKER])

        print(df.info())

        return df.to_html()


def get_symbol(ticker):

    if ticker is None:
        return 'Missing parameter: ' + _PARAM_TICKER

    name = pg.get_symbol_name(ticker)

    if name is None:
        return f'Symbol with ticker {ticker} NOT found!'
    else:
        return name[0]


def get_prices_from_alphavantage(ticker, interval, size):

    if ticker is None:
        return 'Missing parameter: ' + _PARAM_TICKER

    if interval is None:
        return 'Missing parameter: ' + _PARAM_INTERVAL

    if size is None:
        return 'Missing parameter: ' + _PARAM_SIZE

    prices = av.get_prices(cfg.AV_APIKEY, ticker, interval, size)

    return prices.to_html()


def is_datetime_string(datetime):

    try:
        dt.datetime.strptime(datetime, '%Y-%m-%d %H:%M')

        return None

    except ValueError as error:

        return str(error)


def is_integer_string(number):

    try:
        int(number)

        return None

    except ValueError as error:

        return str(error)


def get_prices_from_database(ticker, interval, start, end, limit):

    if ticker is None:
        return 'Missing parameter: ' + _PARAM_TICKER

    if interval is None:
        return 'Missing parameter: ' + _PARAM_INTERVAL

    if start is not None:
        error = is_datetime_string(start)

        if error is not None:
            return error
    else:
        return 'Missing parameter: ' + _PARAM_START

    if end is not None:
        error = is_datetime_string(end)

        if error is not None:
            return error

    if limit is not None:
        error = is_integer_string(limit)

        if error is not None:
            return error

    prices = pg.get_prices(ticker, interval, start, end, limit)

    return prices.to_html()


def get_prices_with_features(ticker, interval, start, end, limit):

    if ticker is None:
        return 'Missing parameter: ticker'

    if interval is None:
        return 'Missing parameter: interval'

    if start is not None:
        error = is_datetime_string(start)

        if error is not None:
            return error
    else:
        return 'Missing parameter: ' + _PARAM_START

    if end is not None:
        error = is_datetime_string(end)

        if error is not None:
            return error

    if limit is not None:
        error = is_integer_string(limit)

        if error is not None:
            return error

    prices = pg.get_prices_with_features(ticker, interval, start, end, limit)

    return prices.to_html()


def update_prices(ticker, interval, size):

    if ticker is None:
        return 'Missing parameter: ' + _PARAM_TICKER

    if interval is None:
        return 'Missing parameter: ' + _PARAM_INTERVAL

    if size is None:
        return 'Missing parameter: ' + _PARAM_SIZE

    created, duplicates = pu.update_price(ticker, interval, size)

    return f'{ticker} ({interval}) : {str(created)} created, {str(duplicates)} duplicates'


def get_features(ticker, interval, start, end):

    if ticker is None:
        return 'Missing parameter: ' + _PARAM_TICKER

    if interval is None:
        return 'Missing parameter: ' + _PARAM_INTERVAL

    if start is not None:
        error = is_datetime_string(start)

        if error is not None:
            return error

    if end is not None:
        error = is_datetime_string(end)

        if error is not None:
            return error

    df_features = pg.get_features_by_datetime(ticker, interval, start, end)

    return pd.DataFrame(df_features).to_html()


def update_features(ticker, interval, start, end):

    if ticker is None:
        return 'Missing parameter: ' + _PARAM_TICKER

    if interval is None:
        return 'Missing parameter: ' + _PARAM_INTERVAL

    if start is not None:
        error = is_datetime_string(start)

        if error is not None:
            return error

    if end is not None:
        error = is_datetime_string(end)

        if error is not None:
            return error

    created, duplicates = fu.update_date_features(ticker, interval, start, end)

    return f'{ticker} ({interval}) : {str(created)} created, {str(duplicates)} duplicates'


def get_alphavantage_functions_table():

    df = pd.DataFrame([

        [_VAL_GET_PRICES, f'{_PARAM_TICKER}, {_PARAM_INTERVAL}, {_PARAM_SIZE}'],

        ], columns=[_LBL_FUNCTION, _LBL_PARAMETERS])

    return df.to_html()


def get_database_functions_table():

    df = pd.DataFrame([
            [_VAL_GET_SYMBOL, _PARAM_TICKER],
            [_VAL_GET_ALL_SYMBOLS, ''],

            [_VAL_GET_PRICES, f'{_PARAM_TICKER}, {_PARAM_INTERVAL}, {_PARAM_START}, {_PARAM_END}, {_PARAM_LIMIT}'],
            [_VAL_GET_PRICES_WITH_FEATURES, f'{_PARAM_TICKER}, {_PARAM_INTERVAL}, {_PARAM_START}, {_PARAM_END}, '
                                            f'{_PARAM_LIMIT}'],
            [_VAL_UPDATE_PRICES, f'{_PARAM_TICKER}, {_PARAM_INTERVAL}, {_PARAM_START}, {_PARAM_END}'],

            [_VAL_GET_FEATURES, f'{_PARAM_TICKER}, {_PARAM_INTERVAL},  {_PARAM_START}, {_PARAM_END}'],
            [_VAL_UPDATE_FEATURES, f'{_PARAM_TICKER}, {_PARAM_INTERVAL},  {_PARAM_START}, {_PARAM_END}']
            ], columns=[_LBL_FUNCTION, _LBL_PARAMETERS])

    return df.to_html()


def handle_database_requests(request):

    if request.args and _PARAM_FUNC in request.args:

        func = request.args.get(_PARAM_FUNC)

        print(f'Function detected: {str(func)}')

        ticker = request.args.get(_PARAM_TICKER)
        interval = request.args.get(_PARAM_INTERVAL)
        size = request.args.get(_PARAM_SIZE)
        datetime = request.args.get(_PARAM_DATETIME)
        start = request.args.get(_PARAM_START)
        end = request.args.get(_PARAM_END)
        limit = request.args.get(_PARAM_LIMIT)

        print(f'Parameters detected: ' +
              f'ticker={str(ticker)}, interval={str(interval)}, size={str(size)}, ' +
              f'datetime={datetime}, start={start}, end={end}, limit={limit}')

        if func == _VAL_GET_ALL_SYMBOLS:
            return get_all_symbols()
        elif func == _VAL_GET_SYMBOL:
            return get_symbol(ticker)

        elif func == _VAL_GET_PRICES:
            return get_prices_from_database(ticker, interval, start, end, limit)
        elif func == _VAL_GET_PRICES_WITH_FEATURES:
            return get_prices_with_features(ticker, interval, start, end, limit)
        elif func == _VAL_UPDATE_PRICES:
            return update_prices(ticker, interval, size)

        elif func == _VAL_GET_FEATURES:
            return get_features(ticker, interval, start, end)
        elif func == _VAL_UPDATE_FEATURES:
            return update_features(ticker, interval, start, end)

        else:
            return f'Unknown function: {str(func)}'

    else:

        return f'capsTone version {_VERSION_NO} built {str(dt.datetime.now().timestamp())}<br>' + \
               get_database_functions_table()


def handle_alphavantage_requests(request):

    if request.args and _PARAM_FUNC in request.args:

        func = request.args.get(_PARAM_FUNC)

        print(f'Function detected: {str(func)}')

        ticker = request.args.get(_PARAM_TICKER)
        interval = request.args.get(_PARAM_INTERVAL)
        size = request.args.get(_PARAM_SIZE)

        print(f'Parameters detected: ticker={str(ticker)}, interval={str(interval)}, size={str(size)}')

        if func == _VAL_GET_PRICES:
            return get_prices_from_alphavantage(ticker, interval, size)
        else:
            return f'Unknown function: {str(func)}'
    else:

        return f'capsTone version {_VERSION_NO} built {str(dt.datetime.now().timestamp())}<br>' + \
               get_alphavantage_functions_table()