from db.connection import connect_to_db
import json


def seed_db(env='test'):
    print("\U0001FAB4", "Seeding Database...")
    db = connect_to_db()
    db.run("DROP TABLE if exists treasures")
    db.run("DROP TABLE if exists shops")

    db.run(
        'CREATE TABLE shops (\
        shop_id SERIAL PRIMARY KEY, \
        shop_name VARCHAR(42) NOT NULL, \
        owner VARCHAR(42), \
        slogan VARCHAR (256)\
        )'
    )
    db.run(
        'CREATE TABLE treasures (\
        treasure_id SERIAL PRIMARY KEY,\
        treasure_name VARCHAR(256) NOT NULL,\
        colour VARCHAR (42),\
        age INT,\
        cost_at_auction FLOAT(2),\
        shop_id INT REFERENCES shops(shop_id)\
        )'
    )

    with open(f'data/{env}-data/shops.json', 'r') as file:
        SHOPS_DATA = json.load(file)
        ROWS = SHOPS_DATA['shops']
        row_count = 0
        for row in ROWS:
            db.run(
                'INSERT INTO shops (shop_name, owner, slogan)\
                VALUES (:shop_name, :owner, :slogan)',
                shop_name=row['shop_name'],
                owner=row['owner'],
                slogan=row['slogan']
            )
            row_count += 1
        print(
            f'\U0001F4BE Successfully seeded {row_count} rows to \
            `shops` table in the database. \U0001F44D')

    SHOPS = db.run('SELECT * FROM shops')
    SHOP_IDS = {shop[1]: shop[0] for shop in SHOPS}

    with open(f'data/{env}-data/treasures.json', 'r') as file:
        TREASURES_DATA = json.load(file)
        ROWS = TREASURES_DATA['treasures']
        row_count = 0
        for row in ROWS:
            ROW_VALUES = {
                "treasure_name": row['treasure_name']
                if 'treasure_name' in row else None,
                "colour": row['colour']
                if 'colour' in row else None,
                "age": row['age']
                if 'age' in row else None,
                "cost_at_auction": row['cost_at_auction']
                if 'cost_at_auction' in row else None,
                "shop_id": SHOP_IDS[row['shop']] if 'shop' in row else None,
            }
            db.run(
                'INSERT INTO treasures (treasure_name, colour, age, \
                cost_at_auction, shop_id)\
                VALUES (:treasure_name, :colour, :age,:cost_at_auction, \
                :shop_id)',
                treasure_name=ROW_VALUES['treasure_name'],
                colour=ROW_VALUES['colour'],
                age=ROW_VALUES['age'],
                cost_at_auction=ROW_VALUES['cost_at_auction'],
                shop_id=ROW_VALUES['shop_id']
            )

            row_count += 1
        print(
            f'\U0001F4BE Successfully seeded {row_count} rows to `treasures` \
            table in the database. \U0001F44D')

    db.close()
