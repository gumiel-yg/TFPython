import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from datetime import datetime
from sklearn.linear_model import LinearRegression

# Cargar el dataset con codificación segura
@st.cache_data
def cargar_dataset():
    return pd.read_csv("dataset_depreciacion24051.csv", encoding="latin1")

dataset = cargar_dataset()

# Interfaz
st.title("🧮 Depreciación de Activos - Línea Recta (Bolivia)")
st.subheader("Normativa DS 24051 | Cálculo actual y futuro")

# Entradas del usuario
activo_seleccionado = st.selectbox("Seleccione el tipo de activo:", dataset['nombre_activo'].unique())
valor_compra = st.number_input("Valor de compra del activo (Bs):", min_value=0.0, step=100.0)
fecha_adquisicion = st.date_input("Fecha de adquisición del activo:")

# Procesamiento
vida_util = int(dataset.loc[dataset['nombre_activo'] == activo_seleccionado, 'vida_util'].values[0])
hoy = datetime.now().date()
dias_transcurridos = (hoy - fecha_adquisicion).days
anios_transcurridos_exactos = dias_transcurridos / 365.25
anios_transcurridos = int(min(anios_transcurridos_exactos, vida_util))

depreciacion_anual = valor_compra / vida_util
depreciacion_acumulada = depreciacion_anual * anios_transcurridos
valor_en_libros = max(0.0, valor_compra - depreciacion_acumulada)

# Mostrar resultados
st.write(f"📅 Fecha de hoy: **{hoy}**")
st.write(f"📌 Vida útil del activo: **{vida_util} años**")
st.write(f"⏳ Años transcurridos desde adquisición: **{anios_transcurridos} años**")
st.write(f"💰 Depreciación anual: **Bs {depreciacion_anual:,.2f}**")
st.write(f"📉 Depreciación acumulada: **Bs {depreciacion_acumulada:,.2f}**")
st.write(f"📗 Valor actual en libros: **Bs {valor_en_libros:,.2f}**")

# Generar series para visualización
anios = np.arange(0, vida_util + 1)
valores = np.maximum(valor_compra - depreciacion_anual * anios, 0)
acumuladas = np.minimum(depreciacion_anual * anios, valor_compra)

# Gráfica con seaborn y matplotlib
fig, ax = plt.subplots()
sns.lineplot(x=anios, y=valores, marker='o', label='Valor en Libros', ax=ax)
sns.lineplot(x=anios, y=acumuladas, marker='x', label='Depreciación Acumulada', ax=ax)
ax.set_title("Evolución del Activo: Valor y Depreciación")
ax.set_xlabel("Años desde adquisición")
ax.set_ylabel("Monto (Bs)")
ax.grid(True)
ax.legend()
st.pyplot(fig)

# Modelo predictivo con regresión lineal
X = anios.reshape(-1, 1)
y = valores
modelo = LinearRegression()
modelo.fit(X, y)

anio_futuro = st.slider("Selecciona un año futuro para predecir valor del activo:", 0, vida_util)
valor_predicho = modelo.predict(np.array([[anio_futuro]]))[0]
valor_predicho = max(0, valor_predicho)

st.success(f"🧠 Predicción: Valor estimado del activo en el año {anio_futuro} desde adquisición: **Bs {valor_predicho:,.2f}**")
