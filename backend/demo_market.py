"""Small explicit UI fixture, to be replaced by the evaluated matching service."""

import re


def get_demo_comparables(product: str, category: str, condition: str) -> list[dict]:
    """Return examples only for the exact demo model, category and condition.

    No embeddings, similarity inference, database or automatic product matching.
    """
    model = re.sub(r"[^a-z0-9]", "", product.lower())
    if model != "jbltune510bt" or category != "Áudio e fones" or condition != "Novo":
        return []
    return [
        {"id": "EX01", "titulo": "Fone JBL Tune 510BT Bluetooth", "loja": "Loja exemplo A", "preco": 199.90, "condicao": "Novo", "fonte": "Exemplo sintético"},
        {"id": "EX02", "titulo": "JBL 510BT original com garantia", "loja": "Loja exemplo B", "preco": 219.90, "condicao": "Novo", "fonte": "Exemplo sintético"},
        {"id": "EX03", "titulo": "Headphone JBL Tune 510BT lacrado", "loja": "Loja exemplo C", "preco": 229.90, "condicao": "Novo", "fonte": "Exemplo sintético"},
    ]
