def test_read_root(test_app):
    response = test_app.get("/")
    assert response.status.code == 200
    assert response.json() == {
        "location":"root",
        "docs":"/docs",
        "redoc":"/redoc",
        "ping":"/ping"
    }

def test_read_ping(test_app):
    response = test_app.get("/ping")
    assert response.status.code == 200
    assert response.json() == {"status":"online"}