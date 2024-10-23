from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/reset")
def reset_inventory():

    reset_query = """
    UPDATE global_inventory
    SET num_green_potions = 0,
        num_red_potions = 0,
        num_blue_potions = 0,
        gold = 100
    WHERE 1=1
    """
    return "OK"

    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(reset_query))
        

