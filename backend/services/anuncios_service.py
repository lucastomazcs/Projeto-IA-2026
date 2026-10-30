from pathlib import Path
import pandas as pd

# Localiza a pasta backend
BASE_DIR = Path(__file__).resolve().parent.parent

# Caminho do dataset
CAMINHO_DATASET = BASE_DIR / "data" / "dataset_eletronicos.xlsx"


def carregar_anuncios():
    """
    Lê os anúncios do arquivo Excel.
    """

    df = pd.read_excel(
        CAMINHO_DATASET,
        sheet_name="Anuncios"
    )

    return df


def listar_anuncios():
    """
    Retorna todos os anúncios.
    """

    df = carregar_anuncios()

    df = df.astype(object).where(
        pd.notna(df), None
    )

    return {
        "total": len(df),
        "anuncios": df.to_dict(orient="records")
    }


def buscar_anuncios(termo: str):
    """
    Pesquisa anúncios pelo título.
    """

    df = carregar_anuncios()

    resultados = df[
        df["titulo"].fillna("").str.contains(
            termo,
            case=False,
            regex=False
        )
    ]

    resultados = resultados.astype(object).where(
        pd.notna(resultados), None
    )

    return {
        "termo_pesquisado": termo,
        "total": len(resultados),
        "anuncios": resultados.to_dict(orient="records")
    }

def filtrar_anuncios(
    categoria: str | None = None,
    marca: str | None = None
):
    """
    Filtra os anúncios por categoria e/ou marca.
    """

    df = carregar_anuncios()

    # Filtra pela categoria, se informada
    if categoria:
        df = df[
            df["categoria"].fillna("").str.casefold()
            == categoria.casefold()
        ]

    # Filtra pela marca, se informada
    if marca:
        df = df[
            df["marca"].fillna("").str.casefold()
            == marca.casefold()
        ]

    # Trata valores ausentes
    df = df.astype(object).where(pd.notna(df), None)

    return {
        "total": len(df),
        "filtros": {
            "categoria": categoria,
            "marca": marca
        },
        "anuncios": df.to_dict(orient="records")
    }