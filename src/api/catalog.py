from fastapi import APIRouter

import sqlalchemy
from src import database as db


        
router = APIRouter()

qry = "SELECT num_green_potions, num_red_potions, num_blue_potions, gold FROM global_inventory"


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(qry)).fetchone()
    
    num_green_potions = result[0]
    num_red_potions = result[1]
    num_blue_potions = result[2]
    gold = result[3]

    return [
            {
            "sku": "GREEN_POTION",
            "name": "Green Potion",
            "quantity": num_green_potions,
            "price": 50,
            "potion_type": [0, 100, 0, 0],  
        },
        {
            "sku": "RED_POTION",
            "name": "Red Potion",
            "quantity": num_red_potions,
            "price": 60,
            "potion_type": [100, 0, 0, 0],  
        },
        {
            "sku": "BLUE_POTION",
            "name": "Blue Potion",
            "quantity": num_blue_potions,
            "price": 70,
            "potion_type": [0, 0, 100, 0], 
        }
    ]