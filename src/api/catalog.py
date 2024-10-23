from fastapi import APIRouter

import sqlalchemy
from src import database as db


        
router = APIRouter()
qry = "SELECT gold FROM global_inventory"

@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    with db.engine.begin() as connection:
        result = connection.execute((sqlalchemy.text(qry))).scalar()
    print(result)
    return result
    return [
            {
                "sku": "GREEN_POTION",
                "name": "green potion",
                "quantity": 1,
                "price": 50,
                "potion_type": [0, 100, 0, 0],
            }
        ]
