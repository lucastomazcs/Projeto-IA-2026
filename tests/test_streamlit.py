import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "streamlit_app.py"


class StreamlitTests(unittest.TestCase):
    def app(self):
        return AppTest.from_file(str(APP), default_timeout=20).run()

    def test_form_generates_metrics_and_three_charts(self):
        app = self.app()
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[1].value, "R$ 219,90")
        self.assertEqual(len(app.get("plotly_chart")), 3)

    def test_unknown_model_has_no_market_suggestion(self):
        app = self.app()
        app.text_input(key="product").set_value("JBL Tune 520BT")
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[1].value, "—")
        self.assertEqual(len(app.get("plotly_chart")), 1)
        self.assertTrue(app.warning)

    def test_invalid_input_does_not_keep_old_results(self):
        app = self.app()
        app.button[0].click().run()
        app.number_input(key="fees").set_value(90.0)
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertTrue(app.error)
        self.assertEqual(len(app.metric), 0)

    def test_frontend_query_prefills_and_computes(self):
        app = AppTest.from_file(str(APP), default_timeout=20)
        app.query_params.update({"product":"JBL Tune 510BT", "cost":"150", "shipping":"25", "fees":"10", "margin":"20", "analisar":"1"})
        app.run()
        self.assertFalse(app.exception)
        self.assertEqual(app.number_input(key="cost").value, 150.0)
        self.assertEqual(app.metric[0].value, "R$ 250,00")
        self.assertEqual(app.metric[1].value, "—")


if __name__ == "__main__":
    unittest.main()
