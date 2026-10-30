from fastapi import FastAPI

from backend.routes.anuncios import router as anuncios_router


# Criando a aplicação FastAPI
app = FastAPI(
    title="API de Análise de Concorrência",
    description="Sistema inteligente de comparação de preços de eletrônicos",
    version="1.0.0"
)


# Registrando as rotas dos anúncios
app.include_router(anuncios_router)


# Rota principal
@app.get("/")
def inicio():
    return {
        "mensagem": "API funcionando!",
        "projeto": "Sistema de Análise de Concorrência"
    }


# Rota para verificar o funcionamento
@app.get("/status")
def verificar_status():
    return {
        "status": "online",
        "mensagem": "Backend funcionando corretamente!"
    }