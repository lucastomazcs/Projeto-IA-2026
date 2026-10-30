"""Sentence Transformers matching adapted from the user's Colab export.

The notebook's embedding, cosine-similarity, product-held-out threshold selection,
and hybrid technical checks are exposed here as reusable backend functions.
Exploratory notebook displays, plotting, shell magics and import-time execution
are intentionally left out of the application module.
"""

from __future__ import annotations

import csv
import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

import numpy as np
from sklearn.model_selection import train_test_split


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "sample"
ADS_PATH = DATA_DIR / "anuncios.csv"
CATALOG_PATH = DATA_DIR / "catalogo.csv"
PAIRS_PATH = DATA_DIR / "pares_rotulados.csv"
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
TEST_FRACTION = 0.30
RANDOM_STATE = 42

# Model aliases developed in the Colab notebook, including its later additions.
MODEL_CODES = {
    "JBL_520BT": ("520BT", "520 BT"),
    "JBL_510BT": ("510BT", "510 BT"),
    "SONY_CH520": ("CH520", "CH 520"),
    "SONY_CH720N": ("CH720N", "CH 720N"),
    "LOGITECH_G305": ("G305",),
    "LOGITECH_M170": ("M170",),
    "LOGITECH_C270": ("C270",),
    "JBL_GO3": ("GO3", "GO 3"),
    "JBL_GO4": ("GO4", "GO 4"),
    "LOGITECH_K120": ("K120",),
    "LOGITECH_C920S": ("C920S", "C920 S", "C920S PRO"),
    "KINGSTON_NV2_500GB": ("NV2 500GB", "NV2 500 GB"),
    "KINGSTON_NV2_1TB": ("NV2 1TB", "NV2 1 TB"),
}
KNOWN_BRANDS = (
    "JBL", "SONY", "SAMSUNG", "LOGITECH", "REDRAGON", "KINGSTON",
    "SANDISK", "MOTOROLA", "DELL", "LENOVO", "ACER",
)
KNOWN_LINES = (
    "GALAXY BUDS", "GALAXY TAB", "GALAXY", "OPTIPLEX", "THINKCENTRE",
    "IDEAPAD", "ASPIRE", "ULTRA FLAIR", "EVO PLUS", "LIGHTSYNC",
    "LIGHTSPEED", "KUMARA", "FIZZ", "TUNE", "FLIP", "GO",
)


class MatchingModelError(RuntimeError):
    """Raised when the Sentence Transformers model cannot be loaded or run."""


@lru_cache(maxsize=3)
def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def normalize_words(value: str) -> str:
    value = unicodedata.normalize("NFKD", str(value)).upper()
    value = "".join(character for character in value if not unicodedata.combining(character))
    value = re.sub(r"[^A-Z0-9]+", " ", value)
    return " ".join(value.split())


def normalize_compact(value: str) -> str:
    return normalize_words(value).replace(" ", "")


@lru_cache(maxsize=1)
def _load_model():
    try:
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer(MODEL_NAME, device="cpu")
    except Exception as exc:  # surface model download, cache, and dependency errors clearly
        raise MatchingModelError(
            f"Não foi possível carregar {MODEL_NAME}. Confira as dependências e a conexão inicial."
        ) from exc


@lru_cache(maxsize=1)
def _encoded_ads() -> np.ndarray:
    ads = _read_csv(ADS_PATH)
    titles = [row.get("titulo", "") or "" for row in ads]
    try:
        vectors = _load_model().encode(
            titles,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
            batch_size=32,
        )
        return np.asarray(vectors, dtype=np.float32)
    except MatchingModelError:
        raise
    except Exception as exc:
        raise MatchingModelError("Falha ao gerar embeddings para os anúncios do catálogo.") from exc


def _metrics(labels: list[int], predictions: list[int]) -> dict:
    tp = sum(label == 1 and prediction == 1 for label, prediction in zip(labels, predictions))
    tn = sum(label == 0 and prediction == 0 for label, prediction in zip(labels, predictions))
    fp = sum(label == 0 and prediction == 1 for label, prediction in zip(labels, predictions))
    fn = sum(label == 1 and prediction == 0 for label, prediction in zip(labels, predictions))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1_positive = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    neg_precision = tn / (tn + fn) if tn + fn else 0.0
    neg_recall = tn / (tn + fp) if tn + fp else 0.0
    f1_negative = 2 * neg_precision * neg_recall / (neg_precision + neg_recall) if neg_precision + neg_recall else 0.0
    total = len(labels)
    return {
        "total": total,
        "positives": sum(labels),
        "true_positive": tp,
        "true_negative": tn,
        "false_positive": fp,
        "false_negative": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1_positive,
        "macro_f1": (f1_positive + f1_negative) / 2,
        "accuracy": (tp + tn) / total if total else 0.0,
    }


def _identified_model_codes(title: str) -> set[str]:
    compact = normalize_compact(title)
    return {
        model_id
        for model_id, aliases in MODEL_CODES.items()
        if any(normalize_compact(alias) in compact for alias in aliases)
    }


def _extract_capacities(title: str) -> set[str]:
    normalized = normalize_words(title)
    return {f"{number}{unit}" for number, unit in re.findall(r"\b(\d+)\s*(GB|TB)\b", normalized)}


def _extract_processors(title: str) -> set[str]:
    return set(re.findall(r"\bI[3579]\b", normalize_words(title)))


def _extract_known_term(title: str, terms: tuple[str, ...]) -> str | None:
    normalized = f" {normalize_words(title)} "
    for term in sorted(terms, key=len, reverse=True):
        if f" {normalize_words(term)} " in normalized:
            return term
    return None


def technical_incompatibility(title_1: str, title_2: str) -> bool:
    """Apply the Colab notebook's conservative model/capacity safety rules."""
    codes_1, codes_2 = _identified_model_codes(title_1), _identified_model_codes(title_2)
    if codes_1 and codes_2 and codes_1.isdisjoint(codes_2):
        return True

    for extractor in (_extract_capacities, _extract_processors):
        values_1, values_2 = extractor(title_1), extractor(title_2)
        if values_1 and values_2 and values_1 != values_2:
            return True

    for terms in (KNOWN_BRANDS, KNOWN_LINES):
        term_1 = _extract_known_term(title_1, terms)
        term_2 = _extract_known_term(title_2, terms)
        if term_1 and term_2 and term_1 != term_2:
            return True
    return False


def classify_pair(title_1: str, title_2: str, similarity: float, threshold: float) -> int:
    """Sentence Transformers cosine score plus the notebook's hybrid hard checks."""
    if technical_incompatibility(title_1, title_2):
        return 0
    codes_1, codes_2 = _identified_model_codes(title_1), _identified_model_codes(title_2)
    if codes_1 & codes_2:
        return 1
    return int(float(similarity) >= threshold)


@lru_cache(maxsize=1)
def evaluate_threshold() -> dict:
    """Tune semantic cosine threshold on development products and score held-out products."""
    ads = _read_csv(ADS_PATH)
    pairs = _read_csv(PAIRS_PATH)
    product_ids = list(dict.fromkeys(row["produto_id"] for row in ads))
    development_products, test_products = train_test_split(
        product_ids, test_size=TEST_FRACTION, random_state=RANDOM_STATE
    )
    development_ids, test_ids = set(development_products), set(test_products)
    ads_by_id = {row["anuncio_id"]: (index, row) for index, row in enumerate(ads)}
    embeddings = _encoded_ads()

    def partition_scores(product_set: set[str]) -> tuple[list[float], list[int], list[tuple[str, str]]]:
        scores, labels, titles = [], [], []
        for pair in pairs:
            product_1, product_2 = pair["produto_id_1"], pair["produto_id_2"]
            if product_1 not in product_set or product_2 not in product_set:
                continue
            index_1, row_1 = ads_by_id[pair["anuncio_id_1"]]
            index_2, row_2 = ads_by_id[pair["anuncio_id_2"]]
            score = float(np.dot(embeddings[index_1], embeddings[index_2]))
            scores.append(score)
            labels.append(int(pair["mesmo_produto"]))
            titles.append((row_1["titulo"], row_2["titulo"]))
        return scores, labels, titles

    development_scores, development_labels, development_titles = partition_scores(development_ids)
    best_threshold, best_f1, semantic_dev = 0.30, -1.0, None
    # Match the notebook's 0.30–0.99 sweep and first-maximum tie behavior.
    for step in range(30, 100):
        threshold = step / 100
        predictions = [int(score >= threshold) for score in development_scores]
        metrics = _metrics(development_labels, predictions)
        if metrics["f1"] > best_f1:
            best_threshold, best_f1, semantic_dev = threshold, metrics["f1"], metrics

    def evaluate(scores: list[float], labels: list[int], titles: list[tuple[str, str]]) -> dict:
        semantic = [int(score >= best_threshold) for score in scores]
        hybrid = [classify_pair(left, right, score, best_threshold) for score, (left, right) in zip(scores, titles)]
        return {"semantic": _metrics(labels, semantic), "hybrid": _metrics(labels, hybrid)}

    test_scores, test_labels, test_titles = partition_scores(test_ids)
    return {
        "model": MODEL_NAME,
        "similarity": "cosseno de embeddings normalizados",
        "threshold_selection": "maximização de F1 semântico na divisão de desenvolvimento",
        "threshold": best_threshold,
        "random_state": RANDOM_STATE,
        "test_fraction": TEST_FRACTION,
        "development_products": len(development_ids),
        "test_products": len(test_ids),
        "development_ids": sorted(development_ids),
        "test_ids": sorted(test_ids),
        "development": evaluate(development_scores, development_labels, development_titles),
        "test": evaluate(test_scores, test_labels, test_titles),
    }


def _resolve_product(product: str, category: str, catalog: list[dict[str, str]]) -> dict[str, str] | None:
    query = normalize_compact(product)
    query_words = set(normalize_words(product).split())
    matches = []
    for row in catalog:
        if category and category != "Todas as categorias" and row["categoria"] != category:
            continue
        brand = normalize_words(row["marca"])
        model = normalize_compact(row["modelo"])
        model_alias = _identified_model_codes(row["modelo"])
        query_codes = _identified_model_codes(product)
        has_brand = not brand or brand in query_words
        exact_model = bool(model and model in query)
        code_match = bool(model_alias & query_codes)
        if has_brand and (exact_model or code_match):
            matches.append(row)
    return matches[0] if len(matches) == 1 else None


def match_product(product: str, category: str = "", condition: str = "Novo") -> dict:
    """Resolve one catalog product, embed the query, then return ranked eligible ads."""
    catalog = _read_csv(CATALOG_PATH)
    ads = _read_csv(ADS_PATH)
    resolved = _resolve_product(product, category, catalog)
    if not resolved:
        return {"product": None, "listings": [], "reason": "Modelo não encontrado de forma inequívoca no catálogo."}

    eligible = [
        (index, row) for index, row in enumerate(ads)
        if row["produto_id"] == resolved["produto_id"] and row["condicao"] == condition
    ]
    if not eligible:
        return {"product": resolved, "listings": [], "reason": "Não há anúncios para este modelo e condição."}

    evaluation = evaluate_threshold()
    try:
        query_vector = _load_model().encode(
            [product], convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False
        )[0]
    except MatchingModelError:
        raise
    except Exception as exc:
        raise MatchingModelError("Falha ao gerar o embedding do produto consultado.") from exc

    embeddings = _encoded_ads()
    listings = []
    for index, row in eligible:
        similarity = float(np.dot(query_vector, embeddings[index]))
        if classify_pair(product, row["titulo"], similarity, evaluation["threshold"]):
            listings.append({
                "id": row["anuncio_id"], "titulo": row["titulo"], "loja": row["vendedor"],
                "preco": float(row["preco_brl"]), "condicao": row["condicao"], "fonte": row["origem"],
                "similaridade": similarity,
            })
    listings.sort(key=lambda row: (-row["similaridade"], row["preco"]))
    reason = "" if listings else "Os anúncios ficaram abaixo do limiar de similaridade e das regras técnicas."
    return {"product": resolved, "listings": listings, "reason": reason, "threshold": evaluation["threshold"]}


def available_categories() -> list[str]:
    return sorted({row["categoria"] for row in _read_csv(CATALOG_PATH)})


def available_conditions() -> list[str]:
    return sorted({row["condicao"] for row in _read_csv(ADS_PATH)})


if __name__ == "__main__":
    print(json.dumps(evaluate_threshold(), ensure_ascii=False, indent=2))
