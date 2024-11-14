from pg8000.native import Connection
from dotenv import load_dotenv
import os

load_dotenv()


def connect_to_db():
    return Connection(
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        database=os.getenv("PG_DATABASE"),
        host=os.getenv("PG_HOST"),
        port=int(os.getenv("PG_PORT"))
    )
