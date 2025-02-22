import pytest
import requests

class TestApiHealth:
        
    @pytest.mark.api
    def test_create_book():
        url = "https://run.mocky.io/v3/628dca34-286a-4850-902b-b5fdd89e0ce3/books"  # Replace with your mock API URL
        new_book = {"title": "The Hobbit", "author": "J.R.R. Tolkien"}
        response = requests.post(url, json=new_book)

        assert response.status_code == 201
        assert response.headers["Content-Type"] == "application/json; charset=UTF-8"

        # Check if the book was created (specifics depend on your mock API's response)
        data = response.json()
        assert "id" in data 
        assert data["title"] == "The Hobbit"
        assert data["author"] == "J.R.R. Tolkien"