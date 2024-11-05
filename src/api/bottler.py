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

from fastapi import APIRouter, Depends, HTTPException
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
    potion_type: list[int]  # [Red, Green, Blue, Dark]
    quantity: int


@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):
    """ Handles the delivery of bottled potions, updating inventory and ledger entries. """
    with db.engine.begin() as connection:
        try:
            connection.execute(sqlalchemy.text(
                "INSERT INTO processed (job_id, type) VALUES (:order_id, 'potions')"
            ), {"order_id": order_id})
        except exc.IntegrityError as e:
            return "OK"

    total_ml_subtract = [0, 0, 0, 0]  
    
    with db.engine.begin() as connection:

        trans_id = connection.execute(sqlalchemy.text(
            "INSERT INTO transactions (description, type) VALUES ('Delivering potions, order id :idd', 'bottler deliver') RETURNING id"
        ), {"idd": order_id}).scalar_one()

        for potion in potions_delivered:
            for i in range(4):
                total_ml_subtract[i] -= potion.potion_type[i] * potion.quantity
            
            potion_id = connection.execute(sqlalchemy.text(
                "SELECT id FROM potions WHERE potion_type = :type"
            ), {"type": potion.potion_type}).scalar_one()

            connection.execute(sqlalchemy.text(
                "INSERT INTO ledger_entries (transaction_id, potion_id, quantity_change) VALUES (:trans_id, :potion_id, :quantity)"
            ), {
                "trans_id": trans_id,
                "potion_id": potion_id,
                "quantity": potion.quantity
            })

        connection.execute(sqlalchemy.text(
            "INSERT INTO ledger_entries (transaction_id, item_type, change, description) VALUES "
            "(:trans_id, 'red_ml', :red, 'ML used in bottling'), "
            "(:trans_id, 'green_ml', :green, 'ML used in bottling'), "
            "(:trans_id, 'blue_ml', :blue, 'ML used in bottling'), "
            "(:trans_id, 'dark_ml', :dark, 'ML used in bottling')"
        ), {
            "trans_id": trans_id,
            "red": total_ml_subtract[0],
            "green": total_ml_subtract[1],
            "blue": total_ml_subtract[2],
            "dark": total_ml_subtract[3]
        })

    print(f"Potions delivered: {potions_delivered} order_id: {order_id}")
    return "OK"

@router.post("/plan")
def get_bottle_plan():
    
    with db.engine.begin() as connection:

        ml_inventory = connection.execute(sqlalchemy.text(
            "SELECT COALESCE(SUM(CASE WHEN item_type = 'green_ml' THEN change END), 0), "
            "COALESCE(SUM(CASE WHEN item_type = 'blue_ml' THEN change END), 0), "
            "COALESCE(SUM(CASE WHEN item_type = 'red_ml' THEN change END), 0), "
            "COALESCE(SUM(CASE WHEN item_type = 'dark_ml' THEN change END), 0) "
            "FROM ledger_entries"
        )).fetchone()

        green_ml, blue_ml, red_ml, dark_ml = ml_inventory

        potion_capacity = connection.execute(sqlalchemy.text("SELECT potion_capacity FROM capacity")).scalar_one()
        total_potions = connection.execute(sqlalchemy.text(
            "SELECT COALESCE(SUM(quantity_change), 0) FROM ledger_entries WHERE item_type = 'potion'"
        )).scalar_one()
        
        available_to_make = potion_capacity - total_potions

        res = []
        ml_per_potion = 100  

        if green_ml >= ml_per_potion:
            green_potions_to_make = min(available_to_make, green_ml // ml_per_potion)
            res.append({"potion_type": [0, 100, 0, 0], "quantity": green_potions_to_make})
            available_to_make -= green_potions_to_make
            green_ml -= green_potions_to_make * ml_per_potion

        if red_ml >= ml_per_potion:
            red_potions_to_make = min(available_to_make, red_ml // ml_per_potion)
            res.append({"potion_type": [100, 0, 0, 0], "quantity": red_potions_to_make})
            available_to_make -= red_potions_to_make
            red_ml -= red_potions_to_make * ml_per_potion

        if blue_ml >= ml_per_potion:
            blue_potions_to_make = min(available_to_make, blue_ml // ml_per_potion)
            res.append({"potion_type": [0, 0, 100, 0], "quantity": blue_potions_to_make})
            available_to_make -= blue_potions_to_make
            blue_ml -= blue_potions_to_make * ml_per_potion


        purple_potion_type = [50, 0, 50, 0]  
        if red_ml >= 50 and blue_ml >= 50:
            purple_potions_to_make = min(available_to_make, red_ml // 50, blue_ml // 50)
            res.append({"potion_type": purple_potion_type, "quantity": purple_potions_to_make})
            available_to_make -= purple_potions_to_make
            red_ml -= purple_potions_to_make * 50
            blue_ml -= purple_potions_to_make * 50

        trans_id = connection.execute(sqlalchemy.text(
            "INSERT INTO transactions (description, type) VALUES ('Bottling plan', 'bottling') RETURNING id"
        )).scalar_one()

        for potion in res:
            connection.execute(sqlalchemy.text(
                "INSERT INTO ledger_entries (transaction_id, item_type, change, description) "
                "VALUES (:trans_id, 'potion', :quantity, 'Bottling')"
            ), {"trans_id": trans_id, "quantity": potion["quantity"]})


            if potion["potion_type"] == [0, 100, 0, 0]:
                connection.execute(sqlalchemy.text(
                    "INSERT INTO ledger_entries (transaction_id, item_type, change, description) "
                    "VALUES (:trans_id, 'green_ml', :ml_used, 'ML used in bottling')"
                ), {"trans_id": trans_id, "ml_used": -potion["quantity"] * ml_per_potion})
            elif potion["potion_type"] == [100, 0, 0, 0]:
                connection.execute(sqlalchemy.text(
                    "INSERT INTO ledger_entries (transaction_id, item_type, change, description) "
                    "VALUES (:trans_id, 'red_ml', :ml_used, 'ML used in bottling')"
                ), {"trans_id": trans_id, "ml_used": -potion["quantity"] * ml_per_potion})
            elif potion["potion_type"] == [0, 0, 100, 0]:
                connection.execute(sqlalchemy.text(
                    "INSERT INTO ledger_entries (transaction_id, item_type, change, description) "
                    "VALUES (:trans_id, 'blue_ml', :ml_used, 'ML used in bottling')"
                ), {"trans_id": trans_id, "ml_used": -potion["quantity"] * ml_per_potion})
            elif potion["potion_type"] == purple_potion_type:
                connection.execute(sqlalchemy.text(
                    "INSERT INTO ledger_entries (transaction_id, item_type, change, description) "
                    "VALUES (:trans_id, 'red_ml', :red_ml_used, 'ML used in bottling'), "
                    "(:trans_id, 'blue_ml', :blue_ml_used, 'ML used in bottling')"
                ), {"trans_id": trans_id, "red_ml_used": -potion["quantity"] * 50, "blue_ml_used": -potion["quantity"] * 50})

    return res


