"""Run with: python -m streamlit run streamlit_app.py."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from backend.demo_market import get_demo_comparables
from backend.input_params import CATEGORIES, CONDITIONS, parse_initial_values
from backend.pricing import calculate_minimum_price, recommend_price

st.set_page_config(page_title="Precifica | Análise", page_icon="📊", layout="wide")
st.html("""<style>
    .stMainBlockContainer {max-width:1240px;padding-top:2rem;}
    h1 {letter-spacing:-1px;font-size:2rem!important;}
    [data-testid="stMetric"] {background:white;border:1px solid #e1e6ee;border-radius:7px;padding:16px;}
    [data-testid="stMetricValue"] {font-size:1.65rem;color:#233d64;}
</style>""")


def money(value):
    if value is None:
        return "—"
    return "R$ " + f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def chart_style(figure):
    figure.update_layout(font={"family": "Arial", "color": "#52657f"}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin={"l": 10, "r": 15, "t": 25, "b": 10}, height=330)
    return figure


if "initialized" not in st.session_state:
    initial, errors = parse_initial_values(st.query_params)
    for key, value in initial.items():
        st.session_state[key] = value
    st.session_state.initial_errors = errors
    st.session_state.auto_analyze = st.query_params.get("analisar") == "1" and not errors
    st.session_state.initialized = True

st.caption("PRECIFICA / ANÁLISE E VISUALIZAÇÃO")
st.title("Precificação com contexto")
st.write("Custos, anúncios de referência e gráficos para entender sua operação.")
st.info("Modo de demonstração: cálculos reais, anúncios fictícios. Banco de dados e IA ainda não integrados.")
for message in st.session_state.initial_errors:
    st.warning(message)

left, right = st.columns([1, 2], gap="large")
with left:
    with st.form("pricing_form"):
        st.subheader("Produto e custos")
        product = st.text_input("Nome do produto", key="product", max_chars=120)
        category = st.selectbox("Categoria", CATEGORIES, key="category")
        condition = st.selectbox("Condição", CONDITIONS, key="condition")
        st.divider()
        cost = st.number_input("Custo do produto (R$)", min_value=0.0, max_value=1_000_000.0, step=1.0, key="cost")
        shipping = st.number_input("Frete e outros custos (R$)", min_value=0.0, max_value=1_000_000.0, step=1.0, key="shipping")
        fixed_fee = st.number_input("Tarifa fixa de venda (R$)", min_value=0.0, max_value=1_000_000.0, step=0.5, key="fixed_fee")
        fees = st.number_input("Taxas de venda (%)", min_value=0.0, max_value=99.0, step=0.5, key="fees")
        margin = st.number_input("Margem desejada (%)", min_value=0.0, max_value=99.0, step=0.5, key="margin")
        use_demo = st.checkbox("Usar anúncios de exemplo", value=True)
        st.caption("Exemplos disponíveis apenas para JBL Tune 510BT, categoria Áudio e fones, condição Novo.")
        submitted = st.form_submit_button("Calcular e gerar gráficos", type="primary", width="stretch")

    if submitted or st.session_state.pop("auto_analyze", False):
        # Always consume the initial trigger, including a manual first submission.
        st.session_state.auto_analyze = False
        st.session_state.pop("analysis", None)
        st.session_state.pop("analysis_error", None)
        try:
            if not product.strip():
                raise ValueError("Informe o nome do produto.")
            listings = get_demo_comparables(product, category, condition) if use_demo else []
            result = recommend_price(cost + shipping, fixed_fee, fees / 100, margin / 100, [row["preco"] for row in listings])
            st.session_state.analysis = {"result": result, "listings": listings, "product": product, "cost": cost, "shipping": shipping, "fixed_fee": fixed_fee, "fees": fees, "margin": margin}
        except ValueError as exc:
            st.session_state.analysis_error = str(exc)

with right:
    if "analysis_error" in st.session_state:
        st.error(st.session_state.analysis_error)
    if "analysis" not in st.session_state:
        st.subheader("Sua análise aparece aqui")
        st.write("Preencha os custos e clique em **Calcular e gerar gráficos**. Os dados enviados pela interface comercial preenchem o formulário automaticamente.")
    else:
        a = st.session_state.analysis
        result = a["result"]
        st.subheader(a["product"])
        st.caption("Resultado da última análise enviada. Alterou os campos? Calcule novamente para atualizar os gráficos.")
        metrics = st.columns(3)
        metrics[0].metric("Preço mínimo com margem", money(result.minimum_price))
        metrics[1].metric("Preço sugerido", money(result.suggested_price))
        metrics[2].metric("Mediana dos anúncios", money(result.market_median))
        if result.viable:
            st.success(result.explanation)
            price = result.suggested_price
            profit = price * (1 - a["fees"] / 100) - a["cost"] - a["shipping"] - a["fixed_fee"]
            p1, p2 = st.columns(2)
            p1.metric("Lucro estimado por venda", money(profit))
            p2.metric("Margem sobre a venda", f"{profit / price * 100:.1f}%".replace(".", ","))
        elif not a["listings"]:
            st.warning("Sem anúncios equivalentes neste exemplo. O preço mínimo é calculado pelos custos; não há recomendação de mercado.")
        else:
            st.warning(result.explanation)

        tab_market, tab_costs, tab_margin = st.tabs(["Comparação de preços", "Composição da venda", "Simulação de margem"])
        with tab_market:
            if a["listings"]:
                df = pd.DataFrame(a["listings"])
                fig = go.Figure(go.Bar(x=df["loja"], y=df["preco"], name="Anúncios fictícios", marker_color="#7896bf", hovertemplate="%{x}<br>R$ %{y:.2f}<extra></extra>"))
                fig.add_hline(y=result.minimum_price, line_dash="dash", line_color="#c48444", annotation_text="Mínimo com margem", annotation_position="top left")
                if result.suggested_price is not None:
                    fig.add_hline(y=result.suggested_price, line_dash="dot", line_color="#315c9c", annotation_text="Sugestão: mediana", annotation_position="bottom right")
                fig.update_layout(yaxis_title="Preço (R$)", yaxis_rangemode="tozero")
                st.plotly_chart(chart_style(fig), width="stretch", key="market_chart")
                st.dataframe(df.rename(columns={"titulo":"Anúncio", "loja":"Loja", "preco":"Preço (R$)", "condicao":"Condição", "fonte":"Fonte"}).drop(columns="id"), hide_index=True, width="stretch")
            else:
                st.info("A comparação de preços será exibida quando houver anúncios equivalentes.")
        with tab_costs:
            if result.suggested_price is not None:
                values = [a["cost"], a["shipping"], a["fixed_fee"], result.suggested_price * a["fees"] / 100, profit]
                fig = go.Figure(go.Pie(labels=["Produto", "Frete e outros", "Tarifa fixa", "Taxas percentuais", "Lucro"], values=values, hole=0.65, sort=False, marker_colors=["#233d64", "#7896bf", "#bac9de", "#d6a872", "#5c918b"]))
                st.plotly_chart(chart_style(fig), width="stretch", key="costs_chart")
                st.caption("Cada parcela corresponde a uma parte do preço de venda sugerido.")
            else:
                st.info("A composição da venda depende de uma sugestão viável. Confira a simulação de margem para avaliar os custos.")
        with tab_margin:
            margins = sorted(set([float(value) for value in range(0, 61, 5)] + [a["margin"]]))
            margins = [value for value in margins if value + a["fees"] < 100]
            floors = [calculate_minimum_price(a["cost"] + a["shipping"], a["fixed_fee"], a["fees"] / 100, value / 100) for value in margins]
            fig = go.Figure(go.Scatter(x=margins, y=floors, mode="lines+markers", name="Preço mínimo", line_color="#315c9c"))
            fig.add_vline(x=a["margin"], line_dash="dot", line_color="#98a8bf")
            fig.update_layout(xaxis_title="Margem desejada (%)", yaxis_title="Preço mínimo (R$)", yaxis_rangemode="tozero")
            st.plotly_chart(chart_style(fig), width="stretch", key="margin_chart")
            st.caption("Simulação matemática com custos e taxas constantes. Não é previsão de demanda ou vendas.")

        with st.expander("Como este resultado foi calculado"):
            st.write("Preço mínimo = (produto + frete e outros custos + tarifa fixa) / (1 − taxa percentual − margem). O mínimo monetário é arredondado para cima ao centavo.")
            st.write("Sugestão = mediana dos anúncios equivalentes, desde que alcance o preço mínimo. Se o mercado ficar abaixo desse mínimo, a aplicação sinaliza inviabilidade.")
            st.caption("A seleção atual usa somente um exemplo exato, sem IA e sem pontuação de similaridade. Troque backend/demo_market.py pelo serviço de matching quando ele estiver validado.")
