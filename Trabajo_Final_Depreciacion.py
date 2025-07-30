import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from datetime import datetime, date

# Configuración visual de seaborn
sns.set(style="whitegrid")

# Cargar dataset y normalizar nombres de columnas
@st.cache_data
def cargar_dataset():
    df = pd.read_csv("dataset_depreciacion24051.csv", encoding="latin1")
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

# Calcular depreciación lineal y predicción futura
def calcular_depreciacion_lineal(valor_inicial, vida_util_anios, fecha_adquisicion, fecha_prediccion=None):
    fecha_actual = datetime.today()

    # Convertir a datetime si es tipo date
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

    # Calcular valor en la fecha futura si se proporciona
    valor_predicho = None
    anio_prediccion = None
    if fecha_prediccion:
        if not isinstance(fecha_prediccion, datetime):
            fecha_prediccion = datetime.combine(fecha_prediccion, datetime.min.time())
        anios_prediccion = (fecha_prediccion - fecha_adquisicion).days // 365
        anios_prediccion = min(anios_prediccion, vida_util_anios)
        valor_predicho = valor_inicial - (depreciacion_anual * anios_prediccion)
        anio_prediccion = anios_prediccion

    return depreciacion_anual, valor_actual, depreciacion_acumulada, valores_restantes, valor_predicho, anio_prediccion

# Interfaz Streamlit
def main():
    st.title("📉 Cálculo de Depreciación por Línea Recta en Bolivia")
    st.caption("Basado en el Decreto Supremo N° 24051")

    df = cargar_dataset()
    st.subheader("Vista previa de la tabla de activos:")
    st.dataframe(df)

    activos = df['nombre_generico'].unique()
    activo_seleccionado = st.selectbox("Seleccione el activo fijo:", activos)

    valor_comercial = st.number_input("Ingrese el valor comercial del activo (Bs):", min_value=0.0, format="%.2f")
    fecha_adquisicion = st.date_input("Seleccione la fecha de adquisición del activo:")

    # Nueva funcionalidad: fecha de predicción futura
    fecha_prediccion = st.date_input("Seleccione una fecha futura para predecir la depreciación (opcional):", value=date.today())

    if st.button("Calcular Depreciación"):
        try:
            vida_util = df[df['nombre_generico'] == activo_seleccionado]['vida_util_anos'].values[0]

            dep_anual, valor_actual, dep_acum, valores_restantes, valor_predicho, anio_prediccion = calcular_depreciacion_lineal(
                valor_comercial, vida_util, fecha_adquisicion, fecha_prediccion
            )

            st.success(f"📉 Depreciación anual: Bs {dep_anual:.2f}")
            st.info(f"💰 Valor actual estimado del activo: Bs {valor_actual:.2f}")

            if valor_predicho is not None:
                st.warning(f"🔮 Valor proyectado al {fecha_prediccion.strftime('%d/%m/%Y')}: Bs {valor_predicho:.2f}")

            # Visualización
            fig, ax = plt.subplots(figsize=(10, 5))
            anios = list(range(vida_util + 1))
            sns.lineplot(x=anios, y=valores_restantes, marker="o", label="Valor restante", ax=ax)
            sns.lineplot(x=anios, y=dep_acum, marker="s", label="Depreciación acumulada", ax=ax)

            if anio_prediccion is not None:
                ax.axvline(anio_prediccion, color="red", linestyle="--", label=f"Predicción ({anio_prediccion} años)")
                ax.scatter(anio_prediccion, valor_predicho, color="red", zorder=5)

            ax.set_title("Evolución del Valor del Activo")
            ax.set_xlabel("Años desde adquisición")
            ax.set_ylabel("Monto (Bs)")
            ax.legend()
            st.pyplot(fig)

        except KeyError:
            st.error("❌ No se encontró la columna 'vida_util_anos'. Verifica el archivo CSV.")

if __name__ == "__main__":
    main()
