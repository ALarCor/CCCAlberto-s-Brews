from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth

import sqlalchemy
from src import database as db

        
router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):
    total_green_potions = sum([potion.quantity for potion in potions_delivered if potion.potion_type == [0, 100, 0, 0]])
    total_red_potions = sum([potion.quantity for potion in potions_delivered if potion.potion_type == [100, 0, 0, 0]])
    total_blue_potions = sum([potion.quantity for potion in potions_delivered if potion.potion_type == [0, 0, 100, 0]])

    with db.engine.begin() as connection:
        
        if total_green_potions > 0:
            connection.execute(sqlalchemy.text(
                "INSERT INTO inventory_ledger (item_type, change, description) VALUES ('green_potion', :change, 'Bottles delivered')"
            ), {"change": total_green_potions})
        
        if total_red_potions > 0:
            connection.execute(sqlalchemy.text(
                "INSERT INTO inventory_ledger (item_type, change, description) VALUES ('red_potion', :change, 'Bottles delivered')"
            ), {"change": total_red_potions})

        if total_blue_potions > 0:
            connection.execute(sqlalchemy.text(
                "INSERT INTO inventory_ledger (item_type, change, description) VALUES ('blue_potion', :change, 'Bottles delivered')"
            ), {"change": total_blue_potions})

    return {"status": "success", "total_green_potions_added": total_green_potions,
            "total_red_potions_added": total_red_potions,
            "total_blue_potions_added": total_blue_potions}