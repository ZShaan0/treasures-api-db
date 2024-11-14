'''This module is the entrypoint for the 'Treasures' FastAPI app.'''
from fastapi import FastAPI, HTTPException, Query
from db.connection import connect_to_db
from pydantic import BaseModel
from typing import Annotated
from pg8000.exceptions import DatabaseError

app = FastAPI()

class NewTreasure(BaseModel):
    treasure_name : str
    colour : str
    age : int
    cost_at_auction : float
    shop_id : int

class NewPrice(BaseModel):
    cost_at_auction : float

treasures_columns = ["treasure_id", "treasure_name", "colour",
                     "age", "cost_at_auction", "shop_name"]
order_options = ['asc', 'desc']

@app.get("/api/treasures")
def get_treasures(sort_by: Annotated[str, Query()] = "age",
                  order: Annotated[str, Query()] = 'asc',
                  colour: Annotated[str, Query()] = None,
                  max_age: Annotated[int, Query()] = None,
                  min_age: Annotated[int, Query()] = None):

    if sort_by not in treasures_columns:
        raise HTTPException(status_code=422, detail=f"Invalid sort field: {sort_by}")
    if order not in order_options:
        raise HTTPException(status_code=422, detail=f"Invalid order field: {order}")

    conn = connect_to_db()

    treasures = conn.run(f"""SELECT
                         treasures.treasure_id,
                         treasures.treasure_name,
                         treasures.colour,
                         treasures.age,
                         treasures.cost_at_auction,
                         shops.shop_name
                         FROM treasures
                         JOIN shops ON treasures.shop_id = shops.shop_id
                         ORDER BY {sort_by} {order} """)

    data = [{"treasure_id" : treasure[0],
             "treasure_name" : treasure[1],
             "colour" :  treasure[2],
             "age" :  treasure[3],
             "cost_at_auction" :  treasure[4],
             "shop_name" : treasure[5]} for treasure in treasures]

    if min_age:
        data[:] = [treasure for treasure in data if treasure['age'] >= min_age]
    if max_age:
        data[:] = [treasure for treasure in data if treasure['age'] <= max_age]
    if colour:
        data[:] = [treasure for treasure in data if treasure['colour'] == colour]

    response = {"treasures" : data}

    conn.close()
    return response

@app.post("/api/treasures", status_code=201)
def post_treasure(new_treasure: NewTreasure):

    try:
        conn = connect_to_db()
        new_query = conn.run("""
            INSERT INTO treasures (treasure_name, colour, age, cost_at_auction, shop_id)
            VALUES (:treasure_name, :colour, :age, :cost_at_auction, :shop_id) 
            RETURNING *""",
            treasure_name = new_treasure.treasure_name,
            colour = new_treasure.colour,
            age = new_treasure.age,
            cost_at_auction = new_treasure.cost_at_auction,
            shop_id = new_treasure.shop_id)
        response = {"treasure" : {"treasure_id" : new_query[0][0],
                                  "treasure_name" : new_query[0][1],
                                  "colour" : new_query[0][2],
                                  "age" : new_query[0][3],
                                  "cost_at_auction" : new_query[0][4],
                                  "shop_id" : new_query[0][5]}}
        return response
    except DatabaseError as dberror:
        raise HTTPException(status_code=422, detail=f"shop id {new_treasure.shop_id} is out of range")
    finally:
        conn.close()

@app.patch("/api/treasures/{treasure_id}", status_code=204)
def patch_treasure(treasure_id: int, new_price: NewPrice):
    conn = connect_to_db()

    get_current_price = conn.run("SELECT cost_at_auction FROM treasures WHERE treasure_id = :id", id = treasure_id)
    if new_price.cost_at_auction >= get_current_price[0][0]:
        raise ValueError(f"The current price is {get_current_price[0][0]}, please enter a lower price")

    set_new_price = conn.run(f"""UPDATE treasures
                             SET cost_at_auction = :price
                             WHERE treasure_id = :id
                             RETURNING *""", price = new_price.cost_at_auction, id = treasure_id)
    conn.close()
    
@app.delete("/api/treasures/{treasure_id}", status_code=204)
def delete_treasure(treasure_id: int):
    conn = connect_to_db()
    deleted = conn.run("""DELETE from treasures
                       WHERE treasure_id = :id
                       RETURNING*"""
                       , id = treasure_id)
    if not deleted:
        raise ValueError(f"There is no treasure with id {treasure_id}")
    
    print(f"treasure {treasure_id} has been deleted")
    conn.close()
    return

@app.get("/api/shops")
def get_shops():
    conn = connect_to_db()    
    shops = conn.run('''SELECT shop_id, shop_name, slogan
                     FROM shops
                     ''')

    treasures_cost = conn.run('''
                              SELECT shop_id, SUM(cost_at_auction)
                              FROM treasures 
                              GROUP BY shop_id  
                              ''')

    response = []
    for shop in shops:
        new_shop = {'shop_id': shop[0], 'shop_name': shop[1], 'slogan': shop[2]}

        for stock in treasures_cost:
            if stock[0] == new_shop['shop_id']:
                new_shop['stock value'] = round(stock[1], 2)
        response.append(new_shop)  

    response = {'shops': response}
    conn.close()
    return response


    


    
    




