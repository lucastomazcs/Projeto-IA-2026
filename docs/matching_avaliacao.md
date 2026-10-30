# Avaliação da busca por produtos equivalentes

## Método

Reproduza a avaliação a partir da raiz do repositório com `python -m backend.product_matching` (ou `.venv\Scripts\python.exe -m backend.product_matching` no Windows).

- Dados sintéticos: 492 anúncios, 41 produtos e 3.483 pares rotulados.
- Representação: TF-IDF com palavras e n-gramas de caracteres, seguida de similaridade por cosseno.
- Regra de segurança: quando os dois títulos contêm códigos de modelo numéricos distintos, o par recebe similaridade zero. A tela também exige uma correspondência inequívoca de marca/modelo/categoria no catálogo antes de consultar anúncios.
- Divisão agrupada por produto: semente 42, com 33 produtos para desenvolvimento e 8 para teste. Pares entre grupos são excluídos para evitar vazamento entre partições.
- O limiar foi escolhido por F1 somente no conjunto de desenvolvimento. Os produtos de teste não participaram da escolha.

## Resultado

Limiar selecionado: **0,104914**.

| Partição | Produtos | Pares avaliados | Positivos | Precisão | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
| Desenvolvimento | 33 | 2.685 | 2.178 | 0,9918 | 0,8306 | 0,9040 |
| Teste | 8 | 540 | 528 | 1,0000 | 0,7557 | 0,8608 |

No teste, o modelo acertou 399 pares positivos, não classificou negativos como positivos e deixou de recuperar 129 positivos. A amostra de teste contém apenas 12 negativos, portanto a precisão de 1,00 não demonstra robustez para outros anúncios ou fontes. O forte desequilíbrio entre classes e o caráter sintético dos dados limitam a interpretação das métricas.

## Limitações

- Esta é uma linha de base TF-IDF, não o modelo Sentence Transformers nem o notebook do Colab: o script exportado do Colab não está presente no clone usado para esta integração.
- Produtos desconhecidos ou ambíguos no catálogo são recusados, em vez de receberem uma correspondência aproximada.
- A busca não estima demanda nem vendas; recomendações financeiras usam a mediana dos anúncios encontrados e mantêm explícito o preço mínimo viável.
- Antes de uso comercial, ampliar os negativos no conjunto de teste, revisar os rótulos, obter anúncios de fontes permitidas e repetir a avaliação em produtos e fontes independentes.
