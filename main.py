import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import time

# Configurações do layout do Streamlit
st.set_page_config(page_title="Dashboard API ETL", layout="wide")

# Título do Dashboard
st.title("Dashboard API ETL")

# Subtítulo
st.subheader("Dados em tempo real de uma API")

# Função para simular dados de uma API
def simulate_api_data():
    current_time = pd.Timestamp.now()
    value = np.random.uniform(40, 160)  # Gera um número aleatório entre 40 e 160
    return {"time": current_time, "value": value}

# Inicializando DataFrame para armazenar os dados
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["time", "value"])

# Espaços reservados para KPIs e gráficos
placeholder_kpi = st.empty()
placeholder_realtime = st.empty()
placeholder_alarm = st.empty()

# Loop para atualizar os dados em tempo real
while True:
    # Simular novo dado da API
    new_data = simulate_api_data()
    st.session_state.data = pd.concat(
        [st.session_state.data, pd.DataFrame([new_data])], ignore_index=True
    )

    # Limitar o tamanho do gráfico em tempo real
    recent_data = st.session_state.data.iloc[-50:]  # Últimos 50 registros

    # Cálculos para os KPIs
    current_value = st.session_state.data.iloc[-1]["value"]
    total_records = len(st.session_state.data)

    # Atualizar KPIs
    with placeholder_kpi.container():
        col1, col2 = st.columns(2)
        col1.metric("Valor Atual", f"{current_value:.2f}")
        col2.metric("Total de Registros", total_records)

    # Verificar limites e alarmar
    if current_value < 50 or current_value > 140:
        with placeholder_alarm.container():
            st.error(f"⚠️ Alerta: Valor fora dos limites! ({current_value:.2f})")
    else:
        with placeholder_alarm.container():
            st.success("Tudo dentro dos limites!")

    # Gráfico em tempo real com linhas de corte
    base_chart = alt.Chart(recent_data).encode(
        x=alt.X('time:T', title='Tempo'),
        tooltip=['time:T', 'value:Q']
    )

    realtime_line = base_chart.mark_line(interpolate='basis', color='blue').encode(
        y=alt.Y('value:Q', title='Valor')
    )

    # Linha de corte inferior
    lower_bound = alt.Chart(pd.DataFrame({'y': [50]})).mark_rule(color='red').encode(
        y='y:Q'
    )

    # Linha de corte superior
    upper_bound = alt.Chart(pd.DataFrame({'y': [140]})).mark_rule(color='red').encode(
        y='y:Q'
    )

    combined_chart = (realtime_line + lower_bound + upper_bound).properties(
        title="Gráfico em Tempo Real com Linhas de Corte",
        width=800,
        height=400
    )

    # Renderizar gráfico no Streamlit
    with placeholder_realtime.container():
        st.altair_chart(combined_chart, use_container_width=True)

    # Taxa de atualização: 0.25 segundos
    time.sleep(0.25)
