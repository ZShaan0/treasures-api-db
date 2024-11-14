'''This module contains the test suite
for the `Treasures` FastAPI app.'''
from fastapi.testclient import TestClient
from pydantic import BaseModel
from main import app
import pytest
from db.seed import seed_db


@pytest.fixture(autouse = True)
def reset_db():
    seed_db()

@pytest.fixture
def client():
    return TestClient(app)


class TestGetTreasures:
    def test_200_healthy(self, client):
        response = client.get("/api/treasures")
        assert response.status_code == 200
    
    def test_200_get_confirmation_of_treasures(self, client):
        response = client.get("/api/treasures")
        body = response.json()
        assert len(body["treasures"]) == 26
        for treasure in body["treasures"]:
            assert type(treasure["treasure_id"]) == int
            assert type(treasure["treasure_name"]) == str
            assert type(treasure["colour"]) == str
            assert type(treasure["age"]) == int
            assert type(treasure["cost_at_auction"]) == float
            assert type(treasure["shop_name"]) == str

    def test_treasures_in_ascending_age_order(self, client):
        response = client.get("/api/treasures")
        body = response.json()
        for index in range(0, 25):
            assert body["treasures"][index]["age"] <= body["treasures"][index + 1]["age"]

class TestGetSortedTreasures:
    def test_200_healthy(self, client):
        response = client.get("/api/treasures?sort_by=cost_at_auction")
        assert response.status_code == 200
    
    def test_200_treasures_ordered_by_auction_cost(self, client):
        response = client.get("/api/treasures?sort_by=cost_at_auction")
        assert response.status_code == 200
        body = response.json()
        for index in range(0, 25):
            assert body["treasures"][index]["cost_at_auction"] <= body["treasures"][index + 1]["cost_at_auction"]
    
    def test_raises_exception_for_invalid_input(self, client):
        response = client.get("/api/treasures?sort_by=cost")
        assert response.status_code == 422

class TestGetOrderedTreasures:
    def test_200_healthy(self, client):
        response = client.get("/api/treasures?order=desc")
        assert response.status_code == 200

    def test_200_treasures_ordered_by_descending(self, client):
        response = client.get("/api/treasures?order=desc")
        assert response.status_code == 200
        body = response.json()
        for index in range(0, 25):
            assert body["treasures"][index]["age"] >= body["treasures"][index + 1]["age"]

    def test_raises_exception_for_invalid_input(self, client):
        response = client.get("/api/treasures?order=dsc")
        assert response.status_code == 422

    def test_default_order_is_ascending(self, client):
        response = client.get("/api/treasures")
        body = response.json()
        for index in range(0, 25):
            assert body["treasures"][index]["age"] <= body["treasures"][index + 1]["age"]

    def test_colour_filters_list_of_treasures(self, client):
        response = client.get("/api/treasures?colour=silver")
        body = response.json()
        maximum_length = 26
        assert response.status_code == 200
        assert len(body['treasures']) <= maximum_length
        for index in range(len(body['treasures'])):
            assert body["treasures"][index]["colour"] == "silver"

class TestPostNewTreasure:
    def test_201_created(self, client):
        response = client.post("/api/treasures", json = {
                                                        "treasure_name": "Steel Computer",
                                                        "colour": "steel",
                                                        "age": 24,
                                                        "cost_at_auction": "666",
                                                        "shop_id": 1
                                                        })
        body = response.json()
        assert response.status_code == 201

    def test_values_correct_in_response(self, client):
        response = client.post("/api/treasures", json = {
                                                        "treasure_name": "Steel Computer",
                                                        "colour": "steel",
                                                        "age": 24,
                                                        "cost_at_auction": "666",
                                                        "shop_id": 1
                                                        })
        body = response.json()
        assert body["treasure"]["treasure_id"] == 27
        assert body["treasure"]["treasure_name"] == "Steel Computer"
        assert body["treasure"]["colour"] == 'steel'
        assert body["treasure"]["age"] == 24
        assert body["treasure"]["cost_at_auction"] == 666
        assert body["treasure"]["shop_id"] == 1
    
    def test_raises_error_when_foreign_key_out_of_range(self, client):
        response = client.post("/api/treasures", json = {
                                                        "treasure_name": "Steel Computer",
                                                        "colour": "steel",
                                                        "age": 24,
                                                        "cost_at_auction": "666",
                                                        "shop_id": 12
                                                        })
        assert response.status_code == 422
        assert response.json() == {"detail": "shop id 12 is out of range"}
    
class TestPatchTreasureCost:
    def test_204_no_content(self, client):
        response = client.patch("/api/treasures/1", json = {
                                                            "cost_at_auction": 5
                                                            })
        assert response.status_code == 204
    
    def test_value_error_if_patch_price_is_not_lower_than_current_price(self, client):
        with pytest.raises(ValueError, match= "The current price is 20.0, please enter a lower price"):
            response = client.patch("/api/treasures/1", 
                                    json = {"cost_at_auction": 1000000})
            
    def test_delete_reduces_length_of_treasures(self, client):
        
        response = client.get("/api/treasures")
        body = response.json()
        assert len(body["treasures"]) == 26

        client.delete("/api/treasures/1")

        response = client.get("/api/treasures")
        body = response.json()
        assert len(body["treasures"]) == 25
        
class TestGetShops:

    def test_200_healthy(self, client):
        response = client.get("/api/shops")
        assert response.status_code == 200

    def test_200_get_confirmation_of_shops(self, client):
        response = client.get("/api/shops")
        body = response.json()
        assert len(body["shops"]) == 11

        for shop in body["shops"]:
            assert type(shop["shop_id"]) == int
            assert type(shop["shop_name"]) == str
            assert type(shop["slogan"]) == str
            assert type(shop["stock value"]) == float

