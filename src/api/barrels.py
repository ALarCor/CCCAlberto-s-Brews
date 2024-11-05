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
    """ """
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"

@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    
    

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
        # Fetch current inventory and gold
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        inventory = result.fetchone()
        
        if inventory['gold'] >= barrel['cost']:
            # Deduct the cost of the barrel from gold
            new_gold = inventory['gold'] - barrel['cost']
            
            
            potion_column = f"num_{color}_potions"
            ml_column = f"num_{color}_ml"
            
            
            new_ml = inventory[ml_column] + barrel['volume']
            new_potions = inventory[potion_column] + 10  
            
            
            sql = f"""
            UPDATE global_inventory
            SET gold = :new_gold,
                {ml_column} = :new_ml,
                {potion_column} = :new_potions
            """
            connection.execute(sqlalchemy.text(sql), {'new_gold': new_gold, 'new_ml': new_ml, 'new_potions': new_potions})
        else:
            print("Not enough gold to purchase barrel.")


