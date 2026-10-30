import unittest

from backend.product_matching import (
    ADS_PATH,
    CATALOG_PATH,
    PAIRS_PATH,
    _read_csv,
    _split_product_ids,
    evaluate_threshold,
    match_product,
)
from backend.pricing import recommend_price


class ProductMatchingTests(unittest.TestCase):
    def test_csv_dataset_is_available_and_complete(self):
        self.assertEqual(len(_read_csv(ADS_PATH)), 492)
        self.assertEqual(len(_read_csv(CATALOG_PATH)), 41)
        self.assertEqual(len(_read_csv(PAIRS_PATH)), 3483)

    def test_nearby_jbl_models_are_kept_separate(self):
        model_510 = match_product("JBL Tune 510BT", "Fones de ouvido", "Novo")
        model_520 = match_product("JBL Tune 520BT", "Fones de ouvido", "Novo")
        self.assertEqual(model_510["product"]["produto_id"], "P002")
        self.assertEqual(model_520["product"]["produto_id"], "P001")
        self.assertTrue(model_510["listings"])
        self.assertTrue(model_520["listings"])
        self.assertFalse({row["id"] for row in model_510["listings"]} & {row["id"] for row in model_520["listings"]})

    def test_ambiguous_unknown_category_and_condition_do_not_guess(self):
        self.assertIsNone(match_product("JBL Tune 530BT", "Fones de ouvido")["product"])
        self.assertIsNone(match_product("JBL Tune 510BT", "Smartphones")["product"])
        used = match_product("JBL Tune 510BT", "Fones de ouvido", "Usado")
        self.assertEqual(used["listings"], [])

    def test_threshold_is_tuned_and_tested_on_disjoint_product_sets(self):
        result = evaluate_threshold()
        self.assertEqual(result["development_products"], 33)
        self.assertEqual(result["test_products"], 8)
        self.assertFalse(set(result["development_ids"]) & set(result["test_ids"]))
        self.assertGreater(result["threshold"], 0)
        self.assertGreater(result["test"]["f1"], 0.5)

    def test_matching_prices_feed_financial_recommendation(self):
        matching = match_product("JBL Tune 510BT", "Fones de ouvido", "Novo")
        result = recommend_price(135, 0, 0.12, 0.20, [row["preco"] for row in matching["listings"]])
        self.assertIsNotNone(result.market_median)
        self.assertGreater(result.minimum_price, 0)


if __name__ == "__main__":
    unittest.main()
