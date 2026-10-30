import math
import unittest

from backend.input_params import parse_initial_values
from backend.pricing import calculate_minimum_price, recommend_price


class PricingTests(unittest.TestCase):
    def test_margin_is_over_sale_price(self):
        floor = calculate_minimum_price(135, 5, 0.12, 0.20)
        self.assertAlmostEqual((floor * 0.88 - 140) / floor, 0.20)

    def test_market_recommendation_preserves_margin(self):
        result = recommend_price(135, 0, 0.12, 0.20, [199.9, 219.9, 229.9])
        self.assertEqual(result.suggested_price, 219.9)
        self.assertEqual(result.minimum_price, 198.53)
        self.assertGreaterEqual(result.suggested_price, result.minimum_price)

    def test_monetary_floor_rounds_up(self):
        result = recommend_price(100, 0, 0.1, 0.2, [])
        self.assertEqual(result.minimum_price, 142.86)
        self.assertGreaterEqual(result.minimum_price, 100 / 0.7)

    def test_no_market_suggestion_when_cost_is_too_high(self):
        result = recommend_price(400, 0, 0.12, 0.2, [199.9, 219.9])
        self.assertFalse(result.viable)
        self.assertIsNone(result.suggested_price)

    def test_no_equivalents_keeps_cost_floor(self):
        result = recommend_price(135, 0, 0.12, 0.20, [])
        self.assertEqual(result.minimum_price, 198.53)
        self.assertIsNone(result.market_median)
        self.assertIsNone(result.suggested_price)

    def test_invalid_percentages_and_nonfinite_numbers(self):
        for args in [(100, 0, 0.8, 0.2), (-1, 0, 0.1, 0.2), (math.nan, 0, 0.1, 0.2), (math.inf, 0, 0.1, 0.2)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                calculate_minimum_price(*args)
        with self.assertRaises(ValueError):
            recommend_price(100, 0, 0.1, 0.2, [math.nan])

    def test_url_values_are_validated(self):
        values, errors = parse_initial_values({"product":"JBL Tune 510BT", "cost":"120,50", "fees":"12"})
        self.assertFalse(errors)
        self.assertEqual(values["cost"], 120.5)
        for invalid in ["nan", "inf", "-1", "1000001", "invalid"]:
            with self.subTest(value=invalid):
                self.assertTrue(parse_initial_values({"cost": invalid})[1])
        self.assertTrue(parse_initial_values({"fees":"80", "margin":"20"})[1])


if __name__ == "__main__":
    unittest.main()
