"""Product catalog lookup and a reproducible TF-IDF cosine matching baseline."""

from __future__ import annotations

import csv
import json
import math
import random
import re
import unicodedata
from collections import Counter
from functools import lru_cache
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "sample"
ADS_PATH = DATA_DIR / "anuncios.csv"
CATALOG_PATH = DATA_DIR / "catalogo.csv"
PAIRS_PATH = DATA_DIR / "pares_rotulados.csv"


@lru_cache(maxsize=3)
def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def normalize(value: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode()
    return " ".join(re.findall(r"[a-z0-9]+", ascii_text.lower()))


def _compact(value: str) -> str:
    return normalize(value).replace(" ", "")


def _model_code(value: str) -> str:
    """Extract digit-bearing model tokens while tolerating spaces (510 BT)."""
    normalized = normalize(value)
    pieces = normalized.split()
    codes = []
    index = 0
    while index < len(pieces):
        token = pieces[index]
        if any(char.isdigit() for char in token):
            if index + 1 < len(pieces) and pieces[index + 1].isalpha() and len(pieces[index + 1]) <= 4:
                token += pieces[index + 1]
                index += 1
            codes.append(token)
        index += 1
    return " ".join(codes)


def _document_features(text: str) -> Counter[str]:
    normalized = normalize(text)
    words = normalized.split()
    compact = "".join(words)
    features: Counter[str] = Counter(f"w:{word}" for word in words)
    for size in (2, 3, 4):
        features.update(f"c:{compact[start:start + size]}" for start in range(max(0, len(compact) - size + 1)))
    return features


class TfidfCosine:
    """Small dependency-free TF-IDF vectorizer for title similarity."""

    def __init__(self, documents: list[str]):
        self.document_count = max(1, len(documents))
        frequencies: Counter[str] = Counter()
        for document in documents:
            frequencies.update(_document_features(document).keys())
        self.idf = {
            feature: math.log((1 + self.document_count) / (1 + count)) + 1
            for feature, count in frequencies.items()
        }

    def vector(self, text: str) -> dict[str, float]:
        counts = _document_features(text)
        return {
            feature: (1 + math.log(count)) * self.idf[feature]
            for feature, count in counts.items()
            if feature in self.idf
        }

    def similarity(self, first: str, second: str) -> float:
        # Different digit-bearing model codes are a hard mismatch (e.g. 510BT/520BT).
        first_code, second_code = _model_code(first), _model_code(second)
        if first_code and second_code and first_code != second_code:
            return 0.0
        left, right = self.vector(first), self.vector(second)
        left_norm = math.sqrt(sum(value * value for value in left.values()))
        right_norm = math.sqrt(sum(value * value for value in right.values()))
        if not left_norm or not right_norm:
            return 0.0
        dot = sum(value * right.get(feature, 0.0) for feature, value in left.items())
        return dot / (left_norm * right_norm)


def _listing_text(row: dict[str, str]) -> str:
    return f"{row.get('titulo', '')} {row.get('descricao', '')}"


def _split_product_ids(catalog: list[dict[str, str]], test_fraction: float = 0.2, seed: int = 42) -> tuple[set[str], set[str]]:
    product_ids = sorted(row["produto_id"] for row in catalog)
    shuffled = product_ids.copy()
    random.Random(seed).shuffle(shuffled)
    test_count = max(1, round(len(shuffled) * test_fraction))
    test_ids = set(shuffled[:test_count])
    return set(product_ids) - test_ids, test_ids


def _binary_metrics(labels: list[int], predictions: list[int]) -> dict[str, float | int]:
    tp = sum(label == 1 and prediction == 1 for label, prediction in zip(labels, predictions))
    fp = sum(label == 0 and prediction == 1 for label, prediction in zip(labels, predictions))
    fn = sum(label == 1 and prediction == 0 for label, prediction in zip(labels, predictions))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"total": len(labels), "positives": sum(labels), "true_positive": tp, "false_positive": fp,
            "false_negative": fn, "precision": precision, "recall": recall, "f1": f1}


@lru_cache(maxsize=1)
def evaluate_threshold() -> dict:
    """Tune threshold on development products, then report a product-held-out test."""
    ads = _read_csv(ADS_PATH)
    catalog = _read_csv(CATALOG_PATH)
    pairs = _read_csv(PAIRS_PATH)
    development_ids, test_ids = _split_product_ids(catalog)
    ads_by_id = {row["anuncio_id"]: row for row in ads}
    training_texts = [_listing_text(row) for row in ads if row["produto_id"] in development_ids]
    model = TfidfCosine(training_texts)

    def prepare(product_ids: set[str]) -> tuple[list[float], list[int]]:
        scores, labels = [], []
        for pair in pairs:
            first_id, second_id = pair["produto_id_1"], pair["produto_id_2"]
            if first_id not in product_ids or second_id not in product_ids:
                continue
            first, second = ads_by_id[pair["anuncio_id_1"]], ads_by_id[pair["anuncio_id_2"]]
            scores.append(model.similarity(first["titulo"], second["titulo"]))
            labels.append(int(pair["mesmo_produto"]))
        return scores, labels

    development_scores, development_labels = prepare(development_ids)
    candidates = sorted({0.0, 1.0, *development_scores})
    best = None
    for threshold in candidates:
        metrics = _binary_metrics(development_labels, [int(score >= threshold) for score in development_scores])
        rank = (metrics["f1"], metrics["precision"], threshold)
        if best is None or rank > best[0]:
            best = (rank, threshold, metrics)

    threshold = best[1]
    test_scores, test_labels = prepare(test_ids)
    test_metrics = _binary_metrics(test_labels, [int(score >= threshold) for score in test_scores])
    return {
        "model": "TF-IDF de palavras e n-gramas de caracteres + similaridade de cosseno",
        "seed": 42,
        "development_products": len(development_ids),
        "test_products": len(test_ids),
        "development_ids": sorted(development_ids),
        "test_ids": sorted(test_ids),
        "threshold": threshold,
        "development": best[2],
        "test": test_metrics,
    }


def _resolve_product(product: str, category: str, catalog: list[dict[str, str]]) -> dict[str, str] | None:
    query = _compact(product)
    query_words = set(normalize(product).split())
    matches = []
    for row in catalog:
        if category and category != "Todas as categorias" and row["categoria"] != category:
            continue
        brand = normalize(row["marca"])
        model = _compact(row["modelo"])
        model_code = _model_code(row["modelo"])
        has_brand = not brand or brand in query_words
        exact_model = model and model in query
        code_match = model_code and _compact(model_code) in query and has_brand
        if has_brand and (exact_model or code_match):
            matches.append(row)
    # Avoid guessing if a short model code maps to multiple catalog entries.
    return matches[0] if len(matches) == 1 else None


def match_product(product: str, category: str = "", condition: str = "Novo") -> dict:
    """Resolve a product without conflating similar model numbers, then rank its ads."""
    catalog = _read_csv(CATALOG_PATH)
    ads = _read_csv(ADS_PATH)
    resolved = _resolve_product(product, category, catalog)
    if not resolved:
        return {"product": None, "listings": [], "reason": "Modelo não encontrado de forma inequívoca no catálogo."}

    eligible = [row for row in ads if row["produto_id"] == resolved["produto_id"] and row["condicao"] == condition]
    if not eligible:
        return {"product": resolved, "listings": [], "reason": "Não há anúncios para este modelo e condição."}

    evaluation = evaluate_threshold()
    dev_ids, _ = _split_product_ids(catalog)
    scorer = TfidfCosine([_listing_text(row) for row in ads if row["produto_id"] in dev_ids])
    canonical = f"{resolved['marca']} {resolved['modelo']} {resolved.get('variante', '')}"
    listings = []
    for row in eligible:
        score = scorer.similarity(canonical, row["titulo"])
        if score >= evaluation["threshold"]:
            listings.append({
                "id": row["anuncio_id"], "titulo": row["titulo"], "loja": row["vendedor"],
                "preco": float(row["preco_brl"]), "condicao": row["condicao"], "fonte": row["origem"],
                "similaridade": score,
            })
    listings.sort(key=lambda row: (-row["similaridade"], row["preco"]))
    reason = "" if listings else "Os anúncios do catálogo ficaram abaixo do limiar de similaridade avaliado."
    return {"product": resolved, "listings": listings, "reason": reason, "threshold": evaluation["threshold"]}


def available_categories() -> list[str]:
    return sorted({row["categoria"] for row in _read_csv(CATALOG_PATH)})


def available_conditions() -> list[str]:
    return sorted({row["condicao"] for row in _read_csv(ADS_PATH)})


if __name__ == "__main__":
    print(json.dumps(evaluate_threshold(), ensure_ascii=False, indent=2))
