

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math

import sqlalchemy
from src import database as db

router = APIRouter(

    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/audit")
def get_inventory():
    with db.engine.begin() as connection:
        audit_data = {
            "gold": connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(change), 0) FROM inventory_ledger WHERE item_type = 'gold'")).scalar(),
            "number_of_potions": connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(change), 0) FROM inventory_ledger WHERE item_type = 'potion'")).scalar(),
            "ml_in_barrels": connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(change), 0) FROM inventory_ledger WHERE item_type = 'ml'")).scalar(),
        }
    return audit_data


@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return {
        "potion_capacity": 0,
        "ml_capacity": 0
        }

class CapacityPurchase(BaseModel):
    potion_capacity: int
    ml_capacity: int


@router.post("/deliver/{order_id}")
def deliver_capacity_plan(capacity_purchase : CapacityPurchase, order_id: int):
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return "OK"
