from fastapi import APIRouter

import sqlalchemy
from src import database as db


        
router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute))

    return [
            {
                "sku": "SMALL_GREEN_BARREL",
                "name": "green potion",
                "quantity": 1,
                "price": 100,
                "potion_type": [0, 1, 0, 0],
            }
        ]
