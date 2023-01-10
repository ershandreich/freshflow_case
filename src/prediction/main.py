import pickle

import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LinearRegression

from ..schemas import PredictionRequest


def get_prediction(request: PredictionRequest, data: pd.DataFrame) -> float:
    prepared_request = prepare_features(request=request, data=data)
    model: LinearRegression = pickle.load(open(f'src/models/{request.item_number}_model.sav', 'rb'))
    array_request = prepared_request.drop(['sales_quantity']).values.reshape(1,-1)
    prediction = model.predict(array_request)
    return max(0, int(prediction[0]))


def prepare_features(request: PredictionRequest, data: pd.DataFrame) -> pd.Series:
    data = data.append(dict(request), ignore_index=True)
    request_row_idx = data.index.max()

    data['day'] = pd.to_datetime(data['day'])

    data['day_of_week'] = data.day.dt.day_of_week
    data['is_weekend'] = data.day_of_week.apply(lambda x: 0 if x < 5 else 1)
    data['month'] = data.day.dt.month

    data.set_index('day', inplace=True)

    bins = [-1, 0, 20, 40, 100]
    data['orders_quantity_binned'] = pd.cut(data['orders_quantity'], bins)
    data.drop(['orders_quantity'], axis=1, inplace=True)

    data['price_diff'] = data['suggested_retail_price'] - data['purchase_price']
    data.drop(['suggested_retail_price', 'purchase_price'], axis=1, inplace=True)

    data['sales_lag_1'] = data.sales_quantity.shift(1)
    data['sales_lag_7'] = data.sales_quantity.shift(7)

    data['ma_7'] = data.sales_quantity.rolling(7).mean().shift()
    data['ma_30'] = data.sales_quantity.rolling(30).mean().shift()

    day_of_week_sales, weekend_sales, month_sales = _calculate_sales_features(df=data)
    data = pd.merge(data, day_of_week_sales, how='left', on='day_of_week')
    data = pd.merge(data, weekend_sales, how='left', on='is_weekend')
    data = pd.merge(data, month_sales, how='left', on='month')

    categ_cols = ['day_of_week', 'is_weekend', 'month', 'orders_quantity_binned']
    for col in categ_cols:
        data[col] = data[col].astype(str)

    encoder: OneHotEncoder = pickle.load(open(f'src/models/{request.item_number}_encoder.sav', 'rb'))
    dummy_raw = encoder.transform(data[categ_cols]).toarray()
    dummy_df = pd.DataFrame(dummy_raw, columns=encoder.get_feature_names_out(categ_cols))

    data = pd.merge(data, dummy_df, left_index=True, right_index=True)
    data.drop(categ_cols, axis=1, inplace=True)
    data.drop(['item_number', 'item_name'], axis=1, inplace=True)

    return data.iloc[request_row_idx]


def _calculate_sales_features(df: pd.DataFrame):
    day_of_week_sales = df.groupby(['day_of_week'])[['sales_quantity']].mean()
    day_of_week_sales = day_of_week_sales.reset_index().rename(columns={'sales_quantity': 'dow_avg'})

    weekend_sales = df.groupby(['is_weekend'])[['sales_quantity']].mean()
    weekend_sales = weekend_sales.reset_index().rename(columns={'sales_quantity': 'wd_avg'})

    month_sales = df.groupby(['month'])[['sales_quantity']].mean()
    month_sales = month_sales.reset_index().rename(columns={'sales_quantity': 'month_avg'})

    return day_of_week_sales, weekend_sales, month_sales