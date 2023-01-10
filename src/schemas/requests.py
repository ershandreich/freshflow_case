from pydantic import BaseModel, Field, NonNegativeInt

from datetime import date, datetime


class PredictionRequest(BaseModel):
    day: date = Field(...,
                      title="Prediction date",
                      description="Date for prediction",
                      example=datetime.now().date())
    item_number: int = Field(...,
                             title="Unique id of the product",
                             example=80028349)
    item_name: str = Field(None,
                           title="Name of the product",
                           example="Beer")
    purchase_price: NonNegativeInt = Field(...,
                                           title="Supplier official purchase price per unit",
                                           example=1.5)
    suggested_retail_price: NonNegativeInt = Field(...,
                                                   title="Supplier’s suggested retail price per unit",
                                                   example=2)
    orders_quantity: NonNegativeInt = Field(...,
                                            title="Quantity of orders received at the beginning of the day",
                                            example=10)
