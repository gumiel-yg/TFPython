import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from datetime import datetime
from sklearn.linear_model import LinearRegression

# Cargar datasets
@st.cache_data
def cargar_activos():
    return pd.read_csv("dataset_depreciacion24051.csv", encoding="latin1")

@st.cache_data
def cargar_ufv():
    df = pd.read_csv("UFV_BancoCentral.csv", encoding="latin1", parse_dates=["fecha"])
    df['fecha'] = pd.to_datetime(df['fecha'])
    return df

activos_df = cargar_activos()
ufv_df = cargar_ufv()

# Interfaz de usuario
st.title("🧮 Depreciación y Reexpresión UFV - Bolivia")
st.subheader("DS 24051 Art. 22 + Norma Contable Nº 3 (UFV)")

st.markdown("Ingrese hasta **5 activos fijos** para calcular su depreciación actual y futura:")

# Función para obtener UFV por fecha
def get_ufv_by_date(fecha):
    closest_date = ufv_df.iloc[(ufv_df['fecha'] - fecha).abs().argsort()[:1]]
    return float(closest_date['ufv'])

# Inicializar listas
resultados = []

for i in range(1, 6):
    st.markdown(f"### Activo {i}")
    nombre_activo = st.selectbox(f"Nombre del activo {i}", activos_df['nombre_activo'].unique(), key=f"activo_{i}")
    valor_compra = st.number_input(f"Valor de compra (Bs) del activo {i}:", min_value=0.0, step=100.0, key=f"valor_{i}")
    fecha_adq = st.date_input(f"Fecha de adquisición del activo {i}:", key=f"fecha_{i}")

    if valor_compra > 0:
        vida_util = int(activos_df.loc[activos_df['nombre_activo'] == nombre_activo, 'vida_util'].values[0])
        hoy = datetime.now().date()
        fecha_31dic = pd.to_datetime(f"{hoy.year}-12-31").date()

        # Calcular años transcurridos
        dias = (hoy - fecha_adq).days
        anios_trans = int(min(dias // 365, vida_util))

        # Reexpresión UFV
        ufv_inicio = get_ufv_by_date(pd.to_datetime(fecha_adq))
        ufv_actual = get_ufv_by_date(pd.to_datetime(hoy))
        factor_ajuste = ufv_actual / ufv_inicio
        valor_actualizado = valor_compra * factor_ajuste

        # Depreciación lineal
        depreciacion_anual = valor_actualizado / vida_util
        depreciacion_acumulada = depreciacion_anual * anios_trans
        valor_libros = max(0, valor_actualizado - depreciacion_acumulada)

        resultados.append({
            'Activo': nombre_activo,
            'Valor Compra': valor_compra,
            'Fecha Adquisición': fecha_adq,
            'Vida Útil': vida_util,
            'UFV Inicial': ufv_inicio,
            'UFV Actual': ufv_actual,
            'Factor Ajuste': factor_ajuste,
            'Valor Ajustado': valor_actualizado,
            'Depreciación Anual': depreciacion_anual,
            'Años Transcurridos': anios_trans,
            'Depreciación Acumulada': depreciacion_acumulada,
            'Valor en Libros': valor_libros
        })

# Mostrar resultados
if resultados:
    st.subheader("📊 Resultados de Depreciación por Activo")
    df_resultados = pd.DataFrame(resultados)
    st.dataframe(df_resultados.style.format({
        "Valor Compra": "Bs {:,.2f}",
        "Valor Ajustado": "Bs {:,.2f}",
        "Depreciación Anual": "Bs {:,.2f}",
        "Depreciación Acumulada": "Bs {:,.2f}",
        "Valor en Libros": "Bs {:,.2f}",
        "Factor Ajuste": "{:,.4f}",
        "UFV Inicial": "{:,.5f}",
        "UFV Actual": "{:,.5f}"
    }))

    # Gráficos por activo
    for i, r in enumerate(resultados):
        st.markdown(f"#### 📈 Evolución: {r['Activo']}")
        anios = np.arange(0, r['Vida Útil'] + 1)
        valores = np.maximum(r['Valor Ajustado'] - r['Depreciación Anual'] * anios, 0)
        acumuladas = np.minimum(r['Depreciación Anual'] * anios, r['Valor Ajustado'])

        fig, ax = plt.subplots()
        sns.lineplot(x=anios, y=valores, label='Valor en libros', marker='o', ax=ax)
        sns.lineplot(x=anios, y=acumuladas, label='Depreciación acumulada', marker='x', ax=ax)
        ax.set_xlabel("Años desde adquisición")
        ax.set_ylabel("Bs")
        ax.set_title(f"{r['Activo']} - Depreciación UFV")
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)

    # Predicción con regresión lineal
    st.subheader("🤖 Predicción de valor futuro (modelo lineal)")
    activo_pred = st.selectbox("Seleccione activo para predecir valor:", [r['Activo'] for r in resultados])
    activo_data = next(r for r in resultados if r['Activo'] == activo_pred)

    anios = np.arange(0, activo_data['Vida Útil'] + 1)
    valores = np.maximum(activo_data['Valor Ajustado'] - activo_data['Depreciación Anual'] * anios, 0)

    X = anios.reshape(-1, 1)
    y = valores
    modelo = LinearRegression()
    modelo.fit(X, y)

    anio_futuro = st.slider("Seleccione año futuro desde adquisición:", 0, activo_data['Vida Útil'])
    valor_predicho = modelo.predict(np.array([[anio_futuro]]))[0]
    st.success(f"Predicción de valor en el año {anio_futuro}: **Bs {valor_predicho:,.2f}**")
