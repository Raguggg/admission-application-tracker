def test_home_route(client):
    response = client.get("/hello")
    assert response.status_code == 200
    assert b"Hello Flask" in response.data
