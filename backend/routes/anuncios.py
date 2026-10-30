from fastapi import APIRouter, HTTPException

from backend.services.anuncios_service import (
    listar_anuncios,
    buscar_anuncios,
    filtrar_anuncios
)

from backend.services.comparacao_service import comparar_precos


# Agrupa as rotas relacionadas aos anúncios
router = APIRouter(
    prefix="/anuncios",
    tags=["Anúncios"]
)


# Rota para listar todos os anúncios
@router.get("")
def listar():
    return listar_anuncios()


# Rota para pesquisar anúncios pelo título
@router.get("/buscar")
def buscar(termo: str):
    return buscar_anuncios(termo)


# Rota para comparar preços de um produto
@router.get("/comparar/{produto_id}")
def comparar(produto_id: str):

    resultado = comparar_precos(produto_id)

    if resultado is None:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado ou sem preços válidos."
        )

    return resultado

@router.get("/filtrar")
def filtrar(
    categoria: str | None = None,
    marca: str | None = None
):
    return filtrar_anuncios(
        categoria=categoria,
        marca=marca
    )

