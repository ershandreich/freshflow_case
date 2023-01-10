import datetime
import os

import pandas as pd
from fastapi import HTTPException, APIRouter

from ..schemas import PredictionRequest
from ..prediction import get_prediction

router = APIRouter()


@router.post("/prediction")
def prediction(
        request: PredictionRequest
):
    all_models = os.listdir('src/models')
    all_models = set([int(i.split('_')[0]) for i in all_models])
    if request.item_number not in all_models:
        raise HTTPException(status_code=404,
                            detail=f"Unfortunately, we don't have model for product {request.item_number} yet."
                                   f"Try to get prediction for one of products - {all_models}")

    product_data = pd.read_csv(f"src/data/prepared_data/product_{request.item_number}.csv", index_col=0)
    product_data['day'] = pd.to_datetime(product_data['day'])
    last_date = product_data.day.max()
    if (last_date + datetime.timedelta(days=1)).date() != request.day:
        missed_dates = list(pd.date_range(start=last_date + datetime.timedelta(days=1),
                                          end=request.day - datetime.timedelta(days=1)))
        raise HTTPException(status_code=422, detail=f"Missing data for this range of days - {missed_dates}"
                                                    f"Submit missing data by /add_data endpoint")

    pred = get_prediction(request=request, data=product_data)
    return {"sales_quantity": pred}




