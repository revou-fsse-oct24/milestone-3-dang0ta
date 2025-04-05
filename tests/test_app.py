from flask.testing import FlaskClient

def test_ping(client: FlaskClient):
    response = client.get("/")
    assert response.status_code == 200
    assert "application/json" in response.headers.get("content-type")
    response_json = response.get_json()
    assert "status" in response_json
    assert "OK" in response_json["status"]

def test_error_handler(client: FlaskClient):    
    response = client.get("/foo")
    assert response.status_code ==  404
    assert "application/json" in response.headers.get("content-type")
    response_json = response.get_json()
    assert "error" in response_json
    assert "not found" in response_json["error"]