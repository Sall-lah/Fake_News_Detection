import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestIndexEndpoint:
    def test_status_code(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_content_type(self, client):
        response = client.get("/")
        assert "text/html" in response.content_type

    def test_title_present(self, client):
        response = client.get("/")
        assert b"Fake News Detection API" in response.data

    def test_predict_endpoint_listed(self, client):
        response = client.get("/")
        assert b"/predict" in response.data

    def test_info_endpoint_listed(self, client):
        response = client.get("/")
        assert b"/info" in response.data

    def test_curl_example_present(self, client):
        response = client.get("/")
        assert b"curl" in response.data


class TestInfoEndpoint:
    def test_status_code(self, client):
        response = client.get("/info")
        assert response.status_code == 200

    def test_content_type(self, client):
        response = client.get("/info")
        assert "application/json" in response.content_type

    def test_status_ok(self, client):
        response = client.get("/info")
        data = response.get_json()
        assert data["status"] == "ok"

    def test_name_present(self, client):
        response = client.get("/info")
        data = response.get_json()
        assert data["name"] == "Fake News Detection API"

    def test_version_present(self, client):
        response = client.get("/info")
        data = response.get_json()
        assert data["version"] == "1.0.0"

    def test_endpoints_listed(self, client):
        response = client.get("/info")
        data = response.get_json()
        assert "GET /" in data["endpoints"]
        assert "GET /info" in data["endpoints"]
        assert "POST /predict" in data["endpoints"]

    def test_predict_request_schema(self, client):
        response = client.get("/info")
        data = response.get_json()
        assert "title" in data["predict_request"]
        assert "text" in data["predict_request"]

    def test_predict_response_schema(self, client):
        response = client.get("/info")
        data = response.get_json()
        assert "status" in data["predict_response"]
        assert "label" in data["predict_response"]


class TestPredictEndpoint:
    def test_valid_prediction(self, client):
        response = client.post(
            "/predict",
            json={"title": "Test Title", "text": "This is a test article about news"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "ok"
        assert data["label"] in ("fake", "true")

    def test_title_only_still_works(self, client):
        response = client.post("/predict", json={"title": "Only Title"})
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "ok"

    def test_empty_payload(self, client):
        response = client.post("/predict", json={})
        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"

    def test_no_json(self, client):
        response = client.post("/predict")
        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"

    def test_real_news_classification(self, client):
        response = client.post(
            "/predict",
            json={
                "title": "As U.S. budget fight looms, Republicans flip their fiscal script",
                "text": "WASHINGTON (Reuters) - The head of a conservative Republican faction in the U.S. Congress, who voted this month for a huge expansion of the national debt to pay for tax cuts, called himself a fiscal conservative on Sunday and urged budget restraint in 2018.",
            },
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "ok"
        assert data["label"] in ("fake", "true")

    def test_fake_news_classification(self, client):
        response = client.post(
            "/predict",
            json={
                "title": "Breaking News",
                "text": "Scientists discover revolutionary clean energy source that will change everything",
            },
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "ok"
        assert data["label"] in ("fake", "true")
