# Avaliação do matching Sentence Transformers

## Implementação

A integração adapta o script `02_matching_produtos_ia.py` exportado do Colab. O módulo reutilizável preserva o modelo `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, embeddings dos títulos, similaridade por cosseno, divisão por produto, ajuste de limiar e as verificações híbridas de código de modelo, capacidade e processador. Células de exploração, gráficos do notebook, `display()` e comandos mágicos do Colab foram retirados do fluxo da aplicação.

Reproduza as métricas na raiz com `python -m backend.product_matching` (Windows: `.venv\Scripts\python.exe -m backend.product_matching`). Na primeira execução, o modelo é baixado para o cache local do Hugging Face.

## Protocolo

- Dados sintéticos: 492 anúncios, 41 produtos e 3.483 pares rotulados.
- Divisão: `train_test_split` por `produto_id`, `test_size=0.30`, `random_state=42`, como no Colab. Foram usados 28 produtos em desenvolvimento e 13 no teste. Pares que cruzam os grupos foram excluídos.
- Limiar: varredura de 0,30 a 0,99 em passos de 0,01; selecionado pelo F1 semântico no conjunto de desenvolvimento.
- Classificador híbrido: após a decisão semântica, rejeita incompatibilidade de códigos de modelo, capacidade ou processador; códigos conhecidos iguais podem recuperar pares com score abaixo do limiar.

## Métricas

Limiar selecionado: **0,33**.

| Partição | Método | Pares | Positivos | Precisão | Recall | F1 | F1 macro | Acurácia |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Desenvolvimento | Cosseno | 2.196 | 1.848 | 0,8675 | 0,9995 | 0,9288 | 0,6235 | 0,8711 |
| Desenvolvimento | Híbrido | 2.196 | 1.848 | 0,9919 | 0,9903 | 0,9911 | 0,9719 | 0,9850 |
| Teste | Cosseno | 918 | 858 | 0,9438 | 0,9977 | 0,9700 | 0,6117 | 0,9423 |
| Teste | Híbrido | 918 | 858 | 0,9873 | 0,9977 | 0,9925 | 0,9377 | 0,9858 |

No teste híbrido, a matriz de confusão foi: **856 verdadeiros positivos, 49 verdadeiros negativos, 11 falsos positivos e 2 falsos negativos**. O teste contém 858 pares positivos e apenas 60 negativos; por isso, métricas de F1/precisão devem ser lidas junto do F1 macro e não generalizadas para dados de produção.

## Limitações

- Os rótulos e anúncios são sintéticos; desempenho em títulos reais e fontes diferentes ainda precisa ser medido.
- A regra híbrida cobre códigos de modelo e atributos presentes no notebook. Produtos com códigos não reconhecidos dependem mais do limiar semântico e podem exigir ampliação das regras.
- O modelo não foi treinado ou ajustado nos pares; é um modelo multilíngue pré-treinado usado para embeddings.
- Os resultados não são previsão de demanda ou vendas. O preço recomendado continua usando o catálogo de anúncios encontrados e o mínimo financeiro calculado separadamente.
