"""Validate the frontend-to-Streamlit handoff without trusting URL values."""

from math import isfinite

CATEGORIES = ["Áudio e fones", "Smartphones", "Informática", "Outros eletrônicos"]
CONDITIONS = ["Novo", "Usado"]
DEFAULTS = {"product": "JBL Tune 510BT", "category": CATEGORIES[0], "condition": "Novo", "cost": 120.0, "shipping": 15.0, "fixed_fee": 0.0, "fees": 12.0, "margin": 20.0}


def parse_initial_values(params) -> tuple[dict, list[str]]:
    values = DEFAULTS.copy()
    errors = []
    if "product" in params:
        product = str(params["product"]).strip()
        if not product or len(product) > 120:
            errors.append("O nome do produto deve ter de 1 a 120 caracteres.")
        else:
            values["product"] = product
    for key, options in [("category", CATEGORIES), ("condition", CONDITIONS)]:
        if key in params:
            if params[key] not in options:
                errors.append(f"Valor inválido para {key}.")
            else:
                values[key] = params[key]
    for key in ["cost", "shipping", "fixed_fee", "fees", "margin"]:
        if key not in params:
            continue
        try:
            value = float(str(params[key]).replace(",", "."))
            maximum = 99.0 if key in ("fees", "margin") else 1_000_000.0
            if not isfinite(value) or not 0 <= value <= maximum:
                raise ValueError
            values[key] = value
        except (TypeError, ValueError):
            errors.append(f"Valor numérico inválido para {key}.")
    if values["fees"] + values["margin"] >= 100:
        errors.append("Taxas e margem devem somar menos que 100%.")
    return values, errors
