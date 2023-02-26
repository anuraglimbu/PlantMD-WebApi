def test_root(test_app):
    response = test_app.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "location":"root",
        "docs":"/docs",
        "redoc":"/redoc",
        "ping":"/ping"
    }

def test_ping(test_app):
    response = test_app.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"status":"online"}