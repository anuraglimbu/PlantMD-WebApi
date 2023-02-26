def test_image(test_app):
    response = test_app.get("/image/")
    assert response.status_code == 422
    assert response.json() == {"detail":"Must pass the image"}