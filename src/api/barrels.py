from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth

import sqlalchemy
from src import database as db



router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):

    for barrel in barrels_delivered:
        total_cost += (barrel.price * barrel.quantity)  

       
        if barrel.potion_type == [0, 1, 0, 0]:  # Green
            total_green_ml += (barrel.ml_per_barrel * barrel.quantity)
        elif barrel.potion_type == [1, 0, 0, 0]:  # Red
            total_red_ml += (barrel.ml_per_barrel * barrel.quantity)
        elif barrel.potion_type == [0, 0, 1, 0]:  # Blue
            total_blue_ml += (barrel.ml_per_barrel * barrel.quantity)
        elif barrel.potion_type == [0, 0, 0, 1]:  # Dark
            total_dark_ml += (barrel.ml_per_barrel * barrel.quantity)
        else:
            raise Exception("Invalid barrel potion type")

    with db.engine.begin() as connection:

        tx_id = connection.execute(sqlalchemy.text(
            "INSERT INTO transactions (description, type) VALUES (:desc, 'barrels_deliver') RETURNING id"
        ), {"desc": f"Delivering barrels, order id: {order_id}"}).scalar_one()

        connection.execute(sqlalchemy.insert(ledger_entries), [
            {"transaction_id": tx_id, "item_type": "green_ml", "change": total_green_ml},
            {"transaction_id": tx_id, "item_type": "blue_ml", "change": total_blue_ml},
            {"transaction_id": tx_id, "item_type": "red_ml", "change": total_red_ml},
            {"transaction_id": tx_id, "item_type": "dark_ml", "change": total_dark_ml}
        ])

        connection.execute(sqlalchemy.insert(ledger_entries), [
            {"transaction_id": tx_id, "item_type": "gold", "change": -total_cost}
        ])

    print(f"Barrels delivered: {barrels_delivered}, Order ID: {order_id}")
    print(f"Total cost deducted: {total_cost} gold")
    return {"status": "success", "total_cost": total_cost, "ml_delivered": {
        "green_ml": total_green_ml,
        "blue_ml": total_blue_ml,
        "red_ml": total_red_ml,
        "dark_ml": total_dark_ml
    }}


@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):

    with db.engine.begin() as connection:
        
        ml_capacity = connection.execute(sqlalchemy.text("SELECT ml_capacity FROM capacity")).scalar_one()
        
        gold = connection.execute(sqlalchemy.text(
            "SELECT COALESCE(SUM(change), 0) FROM ledger_entries WHERE item_type = 'gold'"
        )).scalar()

        ml_totals = connection.execute(sqlalchemy.text(
            """
            SELECT 
                COALESCE(SUM(CASE WHEN item_type = 'green_ml' THEN change END), 0) AS green_ml,
                COALESCE(SUM(CASE WHEN item_type = 'blue_ml' THEN change END), 0) AS blue_ml,
                COALESCE(SUM(CASE WHEN item_type = 'red_ml' THEN change END), 0) AS red_ml,
                COALESCE(SUM(CASE WHEN item_type = 'dark_ml' THEN change END), 0) AS dark_ml
            FROM ledger_entries
            """
        )).fetchone()
        
        green_ml, blue_ml, red_ml, dark_ml = ml_totals
        total_ml = green_ml + blue_ml + red_ml + dark_ml
        print("Total ml in stock:", total_ml)

        dark_exist = False
        large_exist = False
        ml_per_color = 6500  
        
        if ml_capacity - total_ml >= 10000:
            ml_per_color = ml_capacity / 3
            large_exist = any("LARGE" in barrel.sku for barrel in wholesale_catalog)

        gold_to_spend = 0
        res = []
        print("ml per color:", ml_per_color)
        print(f"New mL amount: green: {green_ml}, red: {red_ml}, blue: {blue_ml}, gold: {gold}, dark: {dark_ml}")
        print("New total:", green_ml + red_ml + blue_ml + dark_ml)
        print("Gold spent: ", gold_to_spend)
        
        return res
  
    



def buy_potion_barrel(color):
    barrel_costs = {
        'green': {'cost': 10, 'volume': 100},
        'red': {'cost': 15, 'volume': 80},
        'blue': {'cost': 20, 'volume': 70}
    }
    
    barrel = barrel_costs.get(color)
    if not barrel:
        raise ValueError("Invalid potion color")

    with db.engine.begin() as connection:
        
        current_gold = connection.execute(sqlalchemy.text(
            "SELECT COALESCE(SUM(change), 0) FROM inventory_ledger WHERE item_type = 'gold'"
        )).scalar()

        if current_gold >= barrel['cost']:
            
            connection.execute(sqlalchemy.text(
                "INSERT INTO inventory_ledger (item_type, change, description) VALUES ('gold', :change, 'Purchased barrel')"
            ), {"change": -barrel['cost']})

            
            ml_column = f"{color}_ml"
            connection.execute(sqlalchemy.text(
                "INSERT INTO inventory_ledger (item_type, change, description) VALUES (:ml_column, :change, 'Barrel purchased')"
            ), {"ml_column": ml_column, "change": barrel['volume']})
        else:
            print("Not enough gold to purchase barrel.")

