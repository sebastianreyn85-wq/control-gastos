import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Control Financiero Integral", layout="wide")
st.title("📊 Control de Gastos: Hogar vs. Trabajo")

FILE_NAME = "control_gastos.csv"

if os.path.exists(FILE_NAME):
    df = pd.read_csv(FILE_NAME)
    df['Fecha'] = pd.to_datetime(df['Fecha'])
else:
    df = pd.DataFrame(columns=["Fecha", "Ámbito", "Tipo", "Categoría", "Monto", "Descripción"])

st.sidebar.header("📝 Registrar Transacción")
with st.sidebar.form("transaccion_form", clear_on_submit=True):
    fecha = st.date_input("Fecha", datetime.now())
    ambito = st.selectbox("Ámbito", ["Hogar", "Trabajo"])
    tipo = st.selectbox("Tipo", ["Ingreso", "Gasto"])
    categoria = st.selectbox("Categoría", ["Comida", "Guardería", "Combustible", "Materiales Fontanería", "Electricidad", "Cuota Autónomos", "Impuestos", "Ingresos Trabajo", "Otros"])
    monto = st.number_input("Monto (€)", min_value=0.01, step=0.5)
    descripcion = st.text_input("Descripción breve (opcional)")
    guardar = st.form_submit_button("Guardar Registro")

if guardar:
    nueva_fila = pd.DataFrame([{"Fecha": pd.to_datetime(fecha), "Ámbito": ambito, "Tipo": tipo, "Categoría": categoria, "Monto": monto, "Descripción": descripcion}])
    df = pd.concat([df, nueva_fila], ignore_index=True)
    df.to_csv(FILE_NAME, index=False)
    st.sidebar.success("¡Registro guardado!")
    st.rerun()

if not df.empty:
    df['Año'] = df['Fecha'].dt.year
    df['Año-Mes'] = df['Fecha'].dt.to_period('M').astype(str)
    
    st.markdown("### 🔍 Filtros Globales")
    c1, c2 = st.columns(2)
    with c1:
        filtro_ambito = st.multiselect("Filtrar por Ámbito", ["Hogar", "Trabajo"], default=["Hogar", "Trabajo"])
    with c2:
        anos_disponibles = sorted(df['Año'].unique(), reverse=True)
        filtro_ano = st.selectbox("Seleccionar Año", anos_disponibles)

    df_filtrado = df[(df['Ámbito'].isin(filtro_ambito)) & (df['Año'] == filtro_ano)]

    ingresos_totales = df_filtrado[df_filtrado['Tipo'] == 'Ingreso']['Monto'].sum()
    gastos_totales = df_filtrado[df_filtrado['Tipo'] == 'Gasto']['Monto'].sum()
    ahorro_real = ingresos_totales - gastos_totales

    st.markdown("---")
    st.markdown(f"## 💰 Balance Anual {filtro_ano}")
    m1, m2, m3 = st.columns(3)
    m1.metric("Ingresos Totales", f"{ingresos_totales:,.2f} €")
    m2.metric("Gastos Totales", f"{gastos_totales:,.2f} €", delta=f"-{gastos_totales:,.2f} €", delta_color="inverse")
    m3.metric("Ahorro Neto Real", f"{ahorro_real:,.2f} €")

    st.markdown("---")
    tab1, tab2 = st.tabs(["Evolución de Gastos", "Histórico Completo"])
    
    with tab1:
        df_gastos_m = df_filtrado[df_filtrado['Tipo'] == 'Gasto'].groupby('Año-Mes')['Monto'].sum()
        if not df_gastos_m.empty:
            st.bar_chart(df_gastos_m)
            
    with tab2:
        st.dataframe(df.sort_values(by="Fecha", ascending=False), use_container_width=True)
else:
    st.info("👋 Registra tu primera transacción a la izquierda.")
