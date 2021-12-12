from fastapi.testclient import TestClient
from api import api

client = TestClient(api)


class TestRoot:
    def test_it_says_hello_world(self):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello world! :)"}
