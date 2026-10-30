"""Aplicação integrada Precifica: apresentação, formulário e resultados na mesma tela."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from backend.demo_market import get_demo_comparables
from backend.input_params import CATEGORIES, CONDITIONS, parse_initial_values
from backend.pricing import calculate_minimum_price, recommend_price

st.set_page_config(page_title="Precifica | Análise", page_icon="📊", layout="wide")
st.html("""<style>
.stMainBlockContainer{max-width:1240px;padding-top:1.6rem}
[data-testid="stMetric"]{background:white;border:1px solid #e1e6ee;border-radius:7px;padding:15px}
[data-testid="stMetricValue"]{font-size:1.6rem;color:#233d64}
.hero{background:#eff4fb;border-radius:10px;padding:25px 30px;margin:5px 0 15px}
.hero small{letter-spacing:1.4px;color:#5575a5;font-weight:600}
.hero h2{font-size:2rem;color:#142543;margin:.55rem 0}
.hero p{color:#697b95;margin:0}
.navline{display:flex;justify-content:space-between;border-bottom:1px solid #e1e6ee;padding:8px 0 16px;margin-bottom:16px;color:#53627a;font-size:.9rem}
.navline a{color:#315c9c;text-decoration:none;font-weight:600}
.hero-copy{padding:24px 8px 20px 0}
.hero-copy h1{font-size:clamp(2.5rem,4.4vw,4rem);line-height:1.12;letter-spacing:-2px;color:#142543;margin:.65rem 0 1rem}
.hero-copy h1 strong{font-weight:750}
.hero-checks{display:grid;grid-template-columns:1fr 1fr;gap:8px;color:#52637c;font-size:.88rem;padding:15px 0 20px}
.price-card{background:#fffffff0;border:1px solid #dce5f1;border-radius:10px;padding:16px 19px;margin-top:-100px;position:relative;max-width:410px;box-shadow:0 12px 34px #1c37601a}
.benefit-card{height:100%;background:white;border:1px solid #e1e6ee;border-radius:8px;padding:19px}
</style>""")

def money(value):
    return "—" if value is None else "R$ " + f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def chart_style(fig):
    fig.update_layout(font={"family":"Arial","color":"#52657f"},paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",margin={"l":10,"r":15,"t":25,"b":10},height=330)
    return fig

# Query parameters allow the existing commercial page to open the same application
# with the form prefilled. All following edits, predictions and charts stay here.
if "initialized" not in st.session_state:
    initial, errors = parse_initial_values(st.query_params)
    for key, value in initial.items():
        st.session_state[key] = value
    st.session_state.initial_errors = errors
    st.session_state.auto_analyze = st.query_params.get("analisar") == "1" and not errors
    st.session_state.initialized = True

st.markdown('<div class="navline"><span><strong>precifica</strong>　 ·　 Precificação inteligente</span><a href="#precificacao">COMEÇAR AGORA　 →</a></div>',unsafe_allow_html=True)
hero_copy,hero_image=st.columns([1,1],gap="large",vertical_alignment="center")
with hero_copy:
    st.markdown("""<div class="hero-copy"><small>PRECIFICAÇÃO DE ELETRÔNICOS</small>
<h1>Defina preços<br>que <strong>vendem melhor.</strong></h1>
<p>Transforme dados de custos e anúncios comparáveis em decisões mais claras para o seu negócio.</p>
<div class="hero-checks"><span>✓ Análise de mercado</span><span>✓ Margem em perspectiva</span><span>✓ Custos organizados</span><span>✓ Gráficos na mesma tela</span></div></div>""",unsafe_allow_html=True)
    st.link_button("Começar agora　 →","#precificacao",type="primary",use_container_width=False)
with hero_image:
    st.image("frontend/assets/empreendedora.png",use_container_width=True)
    st.markdown("""<div class="price-card"><small>PRÉVIA ILUSTRATIVA · JBL TUNE 510BT</small>
<h3 style="margin:.35rem 0;color:#142543">R$ 199,90</h3><span style="color:#5575a5">Custos e margem apresentados na análise</span></div>""",unsafe_allow_html=True)
st.markdown('<div id="beneficios"></div>',unsafe_allow_html=True)
st.subheader("Um bom preço considera mais do que a concorrência")
b1,b2,b3=st.columns(3)
for column,title,description in [(b1,"Entenda seus custos","Aquisição, frete, taxas de venda e margem."),(b2,"Compare o produto certo","Veja anúncios equivalentes e diferencie modelos parecidos."),(b3,"Enxergue sua margem","Acompanhe preço mínimo, lucro e composição da venda.")]:
    with column:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.caption(description)
with st.expander("Como funciona"):
    st.markdown("1. Informe o produto e a condição.　 2. Inclua seus custos e a margem.　 3. Clique em **Prever preço** para atualizar métricas e gráficos aqui mesmo.")
st.info("Demonstração acadêmica: cálculos reais e anúncios fictícios. O banco de produtos e a inteligência artificial serão integrados depois.")

for message in st.session_state.initial_errors:
    st.warning(message)

st.markdown('<div id="precificacao"></div>',unsafe_allow_html=True)
st.subheader("Comece sua precificação")
with st.form("pricing_form"):
    row1 = st.columns([2,1,1])
    product = row1[0].text_input("Nome do produto",key="product",max_chars=120)
    category = row1[1].selectbox("Categoria",CATEGORIES,key="category")
    condition = row1[2].selectbox("Condição",CONDITIONS,key="condition")
    cost_col, ship_col, fixed_col, fees_col, margin_col = st.columns(5)
    cost = cost_col.number_input("Custo (R$)",min_value=0.0,max_value=1_000_000.0,step=1.0,key="cost")
    shipping = ship_col.number_input("Frete e outros (R$)",min_value=0.0,max_value=1_000_000.0,step=1.0,key="shipping")
    fixed_fee = fixed_col.number_input("Tarifa fixa (R$)",min_value=0.0,max_value=1_000_000.0,step=0.5,key="fixed_fee")
    fees = fees_col.number_input("Taxas (%)",min_value=0.0,max_value=99.0,step=0.5,key="fees")
    margin = margin_col.number_input("Margem desejada (%)",min_value=0.0,max_value=99.0,step=0.5,key="margin")
    use_demo = st.checkbox("Incluir anúncios de exemplo",value=True)
    st.caption("Três anúncios ilustrativos estão disponíveis para JBL Tune 510BT · Áudio e fones · Novo.")
    submitted = st.form_submit_button("Prever preço",type="primary",width="stretch")

should_analyze = submitted or st.session_state.pop("auto_analyze",False)
if should_analyze:
    st.session_state.auto_analyze=False
    st.session_state.pop("analysis",None)
    st.session_state.pop("analysis_error",None)
    try:
        if not product.strip():
            raise ValueError("Informe o nome do produto.")
        listings = get_demo_comparables(product,category,condition) if use_demo else []
        result = recommend_price(cost+shipping,fixed_fee,fees/100,margin/100,[row["preco"] for row in listings])
        st.session_state.analysis={"result":result,"listings":listings,"product":product,"cost":cost,"shipping":shipping,"fixed_fee":fixed_fee,"fees":fees,"margin":margin}
    except ValueError as exc:
        st.session_state.analysis_error=str(exc)

if "analysis_error" in st.session_state:
    st.error(st.session_state.analysis_error)

if "analysis" not in st.session_state:
    st.markdown("#### Custos, margem e mercado em um só lugar")
    col1,col2,col3=st.columns(3)
    col1.markdown("**01 · Informe os custos**  \nProduto, frete e taxas.")
    col2.markdown("**02 · Defina a margem**  \nEscolha sua margem desejada.")
    col3.markdown("**03 · Confira os gráficos**  \nOs resultados aparecem aqui após prever.")
else:
    a=st.session_state.analysis
    result=a["result"]
    st.divider()
    st.subheader(f"Resultado da previsão · {a['product']}")
    metrics=st.columns(3)
    metrics[0].metric("Preço mínimo com margem",money(result.minimum_price))
    metrics[1].metric("Preço sugerido",money(result.suggested_price))
    metrics[2].metric("Mediana dos anúncios",money(result.market_median))
    profit=None
    if result.viable:
        st.success(result.explanation)
        price=result.suggested_price
        profit=price*(1-a["fees"]/100)-a["cost"]-a["shipping"]-a["fixed_fee"]
        p1,p2=st.columns(2)
        p1.metric("Lucro estimado por venda",money(profit))
        p2.metric("Margem sobre a venda",f"{profit/price*100:.1f}%".replace(".",","))
    elif not a["listings"]:
        st.warning("Sem anúncios equivalentes neste exemplo. O preço mínimo considera custos e margem; não há recomendação de mercado.")
    else:
        st.warning(result.explanation)

    market_tab,cost_tab,margin_tab=st.tabs(["Comparação de preços","Composição da venda","Simulação de margem"])
    with market_tab:
        if a["listings"]:
            df=pd.DataFrame(a["listings"])
            fig=go.Figure(go.Bar(x=df["loja"],y=df["preco"],name="Anúncios fictícios",marker_color="#7896bf",hovertemplate="%{x}<br>R$ %{y:.2f}<extra></extra>"))
            fig.add_hline(y=result.minimum_price,line_dash="dash",line_color="#c48444",annotation_text="Mínimo com margem",annotation_position="top left")
            if result.suggested_price is not None:
                fig.add_hline(y=result.suggested_price,line_dash="dot",line_color="#315c9c",annotation_text="Sugestão: mediana",annotation_position="bottom right")
            fig.update_layout(yaxis_title="Preço (R$)",yaxis_rangemode="tozero")
            st.plotly_chart(chart_style(fig),width="stretch",key="market_chart")
            st.dataframe(df.rename(columns={"titulo":"Anúncio","loja":"Loja","preco":"Preço (R$)","condicao":"Condição","fonte":"Fonte"}).drop(columns="id"),hide_index=True,width="stretch")
        else:
            st.info("A comparação será exibida quando houver anúncios equivalentes para este produto.")
    with cost_tab:
        if result.suggested_price is not None and profit is not None:
            values=[a["cost"],a["shipping"],a["fixed_fee"],result.suggested_price*a["fees"]/100,profit]
            fig=go.Figure(go.Pie(labels=["Produto","Frete e outros","Tarifa fixa","Taxas percentuais","Lucro"],values=values,hole=.65,sort=False,marker_colors=["#233d64","#7896bf","#bac9de","#d6a872","#5c918b"]))
            st.plotly_chart(chart_style(fig),width="stretch",key="costs_chart")
            st.caption("Composição do preço de venda sugerido.")
        else:
            st.info("A composição exige uma sugestão de mercado viável.")
    with margin_tab:
        margins=sorted(set([float(value) for value in range(0,61,5)]+[a["margin"]]))
        margins=[value for value in margins if value+a["fees"]<100]
        floors=[calculate_minimum_price(a["cost"]+a["shipping"],a["fixed_fee"],a["fees"]/100,value/100) for value in margins]
        fig=go.Figure(go.Scatter(x=margins,y=floors,mode="lines+markers",name="Preço mínimo",line_color="#315c9c"))
        fig.add_vline(x=a["margin"],line_dash="dot",line_color="#98a8bf")
        fig.update_layout(xaxis_title="Margem desejada (%)",yaxis_title="Preço mínimo (R$)",yaxis_rangemode="tozero")
        st.plotly_chart(chart_style(fig),width="stretch",key="margin_chart")
        st.caption("Simulação matemática com custos e taxas constantes; não prevê demanda ou vendas.")
    with st.expander("Como os resultados são calculados"):
        st.write("Preço mínimo = (produto + frete + tarifa fixa) / (1 − taxa percentual − margem). O valor é arredondado para cima ao centavo.")
        st.write("O preço sugerido é a mediana dos anúncios equivalentes, se atingir o preço mínimo. Caso contrário, a aplicação sinaliza inviabilidade.")
        st.caption("Os anúncios atuais são exemplos fixos, sem IA ou pontuação de similaridade. O catálogo e o matching serão integrados depois.")

