import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from datetime import datetime

# Configuración visual de seaborn
sns.set(style="whitegrid")

# Función para cargar datos
@st.cache_data
def cargar_dataset():
    df = pd.read_csv("dataset_depreciacion24051.csv", encoding="latin1")
    
    # Normalizar nombres de columnas
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("á", "a")
        .str.replace("é", "e")
        .str.replace("í", "i")
        .str.replace("ó", "o")
        .str.replace("ú", "u")
        .str.replace("ñ", "n")
    )

    return df

# Función para calcular la depreciación lineal
def calcular_depreciacion_lineal(valor_inicial, vida_util_anios, fecha_adquisicion):
    fecha_actual = datetime.today()

    # Convertir a datetime si es date
    if not isinstance(fecha_adquisicion, datetime):
        fecha_adquisicion = datetime.combine(fecha_adquisicion, datetime.min.time())

    anios_transcurridos = (fecha_actual - fecha_adquisicion).days // 365
    anios_transcurridos = min(anios_transcurridos, vida_util_anios)
    depreciacion_anual = valor_inicial / vida_util_anios
    valor_actual = valor_inicial - (depreciacion_anual * anios_transcurridos)

    depreciacion_acumulada = []
    valores_restantes = []

    for anio in range(vida_util_anios + 1):
        depreciacion_acumulada.append(depreciacion_anual * anio)
        valores_restantes.append(valor_inicial - depreciacion_anual * anio)

    return depreciacion_anual, valor_actual, depreciacion_acumulada, valores_restantes

# Interfaz Streamlit
def main():
    st.title("Cálculo de Depreciación por Línea Recta en Bolivia")
    st.write("Basado en el Decreto Supremo N° 24051")

    df = cargar_dataset()
    
    st.write("Columnas del archivo:", df.columns.tolist())  # Mostrar columnas normalizadas
    st.subheader("Vista previa de la tabla de activos:")
    st.dataframe(df)

    activos = df['nombre_generico'].unique()
    activo_seleccionado = st.selectbox("Seleccione el activo fijo:", activos)

    valor_comercial = st.number_input("Ingrese el valor comercial del activo (Bs):", min_value=0.0, format="%.2f")
    fecha_adquisicion = st.date_input("Seleccione la fecha de adquisición del activo:")

    if st.button("Calcular Depreciación"):
        try:
            vida_util = df[df['nombre_generico'] == activo_seleccionado]['vida_util_anos'].values[0]

            dep_anual, valor_actual, dep_acum, valores_restantes = calcular_depreciacion_lineal(
                valor_comercial, vida_util, fecha_adquisicion
            )

            st.success(f"Depreciación anual: Bs {dep_anual:.2f}")
            st.info(f"Valor actual estimado del activo: Bs {valor_actual:.2f}")

            # Visualización
            fig, ax = plt.subplots(figsize=(10, 5))
            anios = list(range(vida_util + 1))
            sns.lineplot(x=anios, y=valores_restantes, marker="o", label="Valor restante", ax=ax)
            sns.lineplot(x=anios, y=dep_acum, marker="s", label="Depreciación acumulada", ax=ax)
            ax.set_title("Depreciación del Activo a lo Largo del Tiempo")
            ax.set_xlabel("Años desde adquisición")
            ax.set_ylabel("Monto (Bs)")
            ax.legend()
            st.pyplot(fig)

        except KeyError:
            st.error("❌ No se encontró la columna 'vida_util_anos'. Revisa los nombres del archivo CSV.")

if __name__ == "__main__":
    main()
