import unittest

from fastapi.testclient import TestClient

from backend.main import app


class BackendApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_status(self):
        response = self.client.get("/status")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "online")

    def test_api_uses_shared_csv_catalog(self):
        response = self.client.get("/anuncios")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total"], 492)

    def test_comparison_route_returns_catalog_prices(self):
        response = self.client.get("/anuncios/comparar/P002")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["quantidade_anuncios"], 12)

    def test_equivalent_route_keeps_neighbor_models_separate(self):
        params = {"produto": "JBL Tune 510BT", "categoria": "Fones de ouvido"}
        response = self.client.get("/anuncios/equivalentes", params=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["product"]["produto_id"], "P002")
        self.assertEqual(len(response.json()["listings"]), 12)

    def test_equivalent_route_returns_not_found_for_unknown_model(self):
        response = self.client.get(
            "/anuncios/equivalentes",
            params={"produto": "JBL Tune 530BT", "categoria": "Fones de ouvido"},
        )
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
