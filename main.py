import streamlit as st
import pandas as pd
import requests
import time
import altair as alt

# Configurações do layout do Streamlit
st.set_page_config(page_title="Dashboard API ETL", layout="wide")

# Título do Dashboard
st.title("Dashboard API ETL")

# Subtítulo
st.subheader("Dados em tempo real de uma API de Cotação")

# Função para obter a cotação
def cotacao(moeda: str):
    response = requests.get(f"https://economia.awesomeapi.com.br/json/last/{moeda}")
    return response.json()

# Função para transformar os dados e pegar o valor de 'high'
def transform(moeda: str):
    cotacao_dados = cotacao(moeda)
    high_valor = cotacao_dados['USDBRL']['high']
    return float(high_valor)  # Convertendo para float

# Inicializando DataFrame para armazenar os dados
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["time", "high"])

# Espaços reservados para KPIs e gráficos
placeholder_kpi = st.empty()
placeholder_realtime = st.empty()
placeholder_alarm = st.empty()

# Loop para atualizar os dados em tempo real
while True:
    # Pegar o valor 'high' da cotação
    high_data = transform('USD-BRL')
    
    # Criar novo dado com o timestamp e o valor 'high'
    new_data = {"time": pd.Timestamp.now(), "high": high_data}
    
    # Atualizar o DataFrame com os novos dados
    st.session_state.data = pd.concat(
        [st.session_state.data, pd.DataFrame([new_data])], ignore_index=True
    )

    # Limitar o tamanho do gráfico em tempo real
    recent_data = st.session_state.data.iloc[-50:]  # Últimos 50 registros

    # Cálculos para os KPIs
    current_value = st.session_state.data.iloc[-1]["high"]
    total_records = len(st.session_state.data)

    # Atualizar KPIs
    with placeholder_kpi.container():
        col1, col2 = st.columns(2)
        col1.metric("Valor Atual (High)", f"{current_value:.2f}")  # Agora o valor é um float
        col2.metric("Total de Registros", total_records)

    # Verificar limites e alarmar
    if current_value < 5.0 or current_value > 6.0:  # Exemplo de limites para o valor 'high'
        with placeholder_alarm.container():
            st.error(f"⚠️ Alerta: Valor fora dos limites! ({current_value:.2f})")
    else:
        with placeholder_alarm.container():
            st.success("Tudo dentro dos limites!")

    # Gráfico em tempo real com linhas de corte
    base_chart = alt.Chart(recent_data).encode(
        x=alt.X('time:T', title='Tempo'),
        tooltip=['time:T', 'high:Q']
    )

    realtime_line = base_chart.mark_line(interpolate='basis', color='blue').encode(
        y=alt.Y('high:Q', title='Valor High')
    )

    # Linha de corte inferior
    lower_bound = alt.Chart(pd.DataFrame({'y': [5.0]})).mark_rule(color='red').encode(
        y='y:Q'
    )

    # Linha de corte superior
    upper_bound = alt.Chart(pd.DataFrame({'y': [6.0]})).mark_rule(color='red').encode(
        y='y:Q'
    )

    combined_chart = (realtime_line + lower_bound + upper_bound).properties(
        title="Gráfico em Tempo Real de Cotação (High)",
        width=800,
        height=400
    )

    # Renderizar gráfico no Streamlit
    with placeholder_realtime.container():
        st.altair_chart(combined_chart, use_container_width=True)

    # Taxa de atualização: 1 segundo
    time.sleep(1)
