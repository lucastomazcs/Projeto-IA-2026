import pandas as pd

from backend.services.anuncios_service import carregar_anuncios


def comparar_precos(produto_id: str):
    """
    Compara os preços dos anúncios de um mesmo produto.

    Retorna:
    - Quantidade de anúncios
    - Menor preço
    - Maior preço
    - Preço médio
    - Diferença entre preços
    """

    # Carrega os anúncios do dataset
    df = carregar_anuncios()

    # Filtra os anúncios do produto informado
    anuncios = df[
        df["produto_id"] == produto_id
    ].copy()

    # Verifica se o produto existe
    if anuncios.empty:
        return None

    # Converte os preços para valores numéricos
    anuncios["preco_brl"] = pd.to_numeric(
        anuncios["preco_brl"],
        errors="coerce"
    )

    # Remove anúncios sem preço válido
    anuncios = anuncios.dropna(subset=["preco_brl"])

    if anuncios.empty:
        return None

    # Calcula as estatísticas
    menor_preco = anuncios["preco_brl"].min()
    maior_preco = anuncios["preco_brl"].max()
    preco_medio = anuncios["preco_brl"].mean()

    return {
        "produto_id": produto_id,
        "quantidade_anuncios": len(anuncios),
        "menor_preco": round(float(menor_preco), 2),
        "maior_preco": round(float(maior_preco), 2),
        "preco_medio": round(float(preco_medio), 2),
        "diferenca_precos": round(
            float(maior_preco - menor_preco), 2
        )
    }