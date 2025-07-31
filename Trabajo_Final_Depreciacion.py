import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from datetime import datetime
from sklearn.linear_model import LinearRegression

# Cargar el dataset
@st.cache_data
def cargar_dataset():
    return pd.read_csv("dataset_depreciacion24051.csv", encoding="latin1")

dataset = cargar_dataset()

# Interfaz de usuario
st.title("Cálculo de Depreciación - Método Línea Recta")
st.subheader("Basado en normativa boliviana DS 24051")

# Entrada de datos
activo_seleccionado = st.selectbox("Seleccione el tipo de activo:", dataset['nombre_activo'].unique())
valor_compra = st.number_input("Ingrese el valor de compra del activo (Bs):", min_value=0.0, step=100.0)
fecha_adquisicion = st.date_input("Fecha de adquisición del activo:")

# Buscar la vida útil del activo
vida_util = dataset.loc[dataset['nombre_activo'] == activo_seleccionado, 'vida_util'].values[0]
anio_actual = datetime.now().year
anio_adquisicion = fecha_adquisicion.year

# Cálculo de depreciación
anios_transcurridos = max(0, min(anio_actual - anio_adquisicion, vida_util))
depreciacion_anual = valor_compra / vida_util
acumulada = depreciacion_anual * anios_transcurridos
valor_libros_actual = max(0, valor_compra - acumulada)

st.write(f"**Vida útil:** {vida_util} años")
st.write(f"**Años transcurridos:** {anios_transcurridos}")
st.write(f"**Depreciación anual:** Bs {depreciacion_anual:,.2f}")
st.write(f"**Depreciación acumulada a {anio_actual}:** Bs {acumulada:,.2f}")
st.write(f"**Valor en libros actual:** Bs {valor_libros_actual:,.2f}")

# Simulación futura
anios = np.arange(0, vida_util + 1)
valores = np.maximum(valor_compra - depreciacion_anual * anios, 0)

# Gráfico de depreciación
fig, ax = plt.subplots()
sns.lineplot(x=anios, y=valores, marker='o', ax=ax)
ax.set_title("Depreciación por Línea Recta")
ax.set_xlabel("Años desde adquisición")
ax.set_ylabel("Valor en libros (Bs)")
ax.grid(True)
st.pyplot(fig)

# Modelo predictivo (simple)
X = anios.reshape(-1, 1)
y = valores
modelo = LinearRegression()
modelo.fit(X, y)

# Comando predict
anio_futuro = st.slider("Seleccione años futuros para predecir valor del activo:", 0, vida_util)
valor_futuro = modelo.predict(np.array([[anio_futuro]]))[0]
st.success(f"Valor estimado del activo dentro de {anio_futuro} años: Bs {valor_futuro:,.2f}")


