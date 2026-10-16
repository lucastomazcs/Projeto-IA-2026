"""Deterministic price calculations for the pricing PoC."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PriceResult:
    minimum_price: float
    suggested_price: float | None
    market_median: float | None
    market_low: float | None
    market_high: float | None
    viable: bool
    explanation: str


def calculate_minimum_price(
    variable_cost: float,
    fixed_fee: float,
    percentage_fee: float,
    target_margin: float,
) -> float:
    """Return minimum sale price for target margin over sale price.

    percentage_fee and target_margin are decimal fractions (e.g. 0.16).
    """
    if variable_cost < 0 or fixed_fee < 0:
        raise ValueError("Custos e tarifas não podem ser negativos.")
    if not 0 <= percentage_fee < 1:
        raise ValueError("A taxa percentual deve estar entre 0 (inclusive) e 1.")
    if not 0 <= target_margin < 1:
        raise ValueError("A margem-alvo deve estar entre 0 (inclusive) e 1.")

    denominator = 1 - percentage_fee - target_margin
    if denominator <= 0:
        raise ValueError("Taxa percentual e margem-alvo devem somar menos que 100%.")

    return (variable_cost + fixed_fee) / denominator


def recommend_price(
    variable_cost: float,
    fixed_fee: float,
    percentage_fee: float,
    target_margin: float,
    comparable_prices: list[float],
) -> PriceResult:
    """Calculate a viable floor and a market-informed recommendation.

    The suggested price is the median of valid comparables, rounded to cents,
    only when it meets the minimum viable price. Otherwise, the result is
    explicitly marked as not viable at the observed market level.
    """
    floor = calculate_minimum_price(
        variable_cost, fixed_fee, percentage_fee, target_margin
    )
    prices = sorted(float(price) for price in comparable_prices if float(price) > 0)
    if not prices:
        return PriceResult(
            minimum_price=round(floor, 2),
            suggested_price=None,
            market_median=None,
            market_low=None,
            market_high=None,
            viable=False,
            explanation="Sem comparáveis válidos; não há sugestão de preço de mercado.",
        )

    middle = len(prices) // 2
    median = prices[middle] if len(prices) % 2 else (prices[middle - 1] + prices[middle]) / 2
    low = prices[max(0, int((len(prices) - 1) * 0.25))]
    high = prices[min(len(prices) - 1, int((len(prices) - 1) * 0.75))]
    viable = median >= floor
    suggestion = round(median, 2) if viable else None
    explanation = (
        "Mediana dos comparáveis atende ao preço mínimo viável."
        if viable
        else "Mercado observado abaixo do preço mínimo viável; venda sinalizada como inviável."
    )

    return PriceResult(
        minimum_price=round(floor, 2),
        suggested_price=suggestion,
        market_median=round(median, 2),
        market_low=round(low, 2),
        market_high=round(high, 2),
        viable=viable,
        explanation=explanation,
    )


if __name__ == "__main__":
    example = recommend_price(
        variable_cost=60,
        fixed_fee=5,
        percentage_fee=0.16,
        target_margin=0.15,
        comparable_prices=[98, 101, 104.90, 110, 115],
    )
    print(example)
