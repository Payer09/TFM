import streamlit as st
import pickle
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO

# Ruta del archivo guardado
ruta_pipeline = 'pipeline_lgb.pkl'

# Cargar el pipeline
with open(ruta_pipeline, 'rb') as file:
    pipeline = pickle.load(file)

# Título de la aplicación
st.title("Herramienta de apoyo para la cirugía de citorreducción")
st.markdown("Esta herramienta predice la probabilidad de que se complete la **citorreducción completa** basada en las características clínicas ingresadas.")

st.sidebar.header("🔧 Parámetros de Entrada:")
# Formularios para los inputs
histologia = st.sidebar.selectbox("Histología", options=["HGSOC", "LGSOC", "Carcinosarcoma ovárico", "Carcinoma mucinoso",
                                  "Carcinoma endometrioide ovárico", "Carcinoma de célula clara", "Adenocarcinoma mesonéfrico"])

mtv_infradia_total = st.sidebar.slider(
    "MTV_INFRADIA_TOTAL", max_value=1500.0, min_value=0.0, value=0.0)
glsupr_mtv = st.sidebar.slider(
    "GLSUPR_MTV", max_value=50.0, min_value=0.0, value=0.0)
tlg_infradia_total = st.sidebar.slider(
    "TLG_INFRADIA_TOTAL", max_value=10000.0, min_value=0.0, value=0.0)
glsupr_tlg = st.sidebar.slider(
    "GLSUPR_TLG", max_value=50.0, min_value=0.0, value=0.0)
suvmax_liqasc = st.sidebar.slider(
    "SUVMAX_LIQASC", max_value=5.0, min_value=0.0, value=0.0)
edad = st.sidebar.slider("Edad", min_value=0, max_value=110, value=50)

# Cálculos automáticos
mtv_total = mtv_infradia_total + glsupr_mtv
tlg_total = tlg_infradia_total + glsupr_tlg

# Botón de predicción
if st.button("📊 Pulse para predecir"):
    # Crear un DataFrame con los datos ingresados
    input_data = pd.DataFrame({
        "Histología": [histologia],
        "MTV_INFRADIA_TOTAL": [mtv_infradia_total],
        "GLSUPR_MTV": [glsupr_mtv],
        "TLG_INFRADIA_TOTAL": [tlg_infradia_total],
        "GLSUPR_TLG": [glsupr_tlg],
        "SUVMAX_LIQASC": [suvmax_liqasc],
        "Edad": [edad],
        "MTV_TOTAL": [mtv_total],
        "TLG_TOTAL": [tlg_total]
    })

    # Realizar la predicción
    prediction = pipeline.predict(input_data)[0]
    prediction_proba = pipeline.predict_proba(input_data)[0, 1]

    # Mostrar los resultados
    st.subheader("🎯 Resultados de la predicción:")
    result_text = "Citorreducción completa" if prediction == 1 else "Citorreducción no completa"
    st.markdown(f"## Predicción: **{result_text}**")

    # Crear gráfico de tarta con Plotly
    fig = go.Figure(
        data=[go.Pie(
            labels=["Citorreducción completa", "Citorredución no completa"],
            values=[prediction_proba, 1 - prediction_proba],
            hole=0.4,  # Gráfico de dona
            marker=dict(colors=["#4CAF50", "#F44336"],
                        line=dict(color="#000000", width=3)),
            hoverinfo="label+percent"
        )]
    )

    fig.update_layout(
        title="Probabilidad de que se complete la citorreducción",
        title_font_size=20,
        showlegend=True
    )

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig)

    # Información adicional
    st.markdown("#### Características ingresadas:")
    st.dataframe(input_data)

    # Crear archivo Excel de los resultados
    result_data = input_data.copy()
    result_data["Predicción"] = result_text
    result_data["Probabilidad"] = prediction_proba

    # Crear archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        result_data.to_excel(writer, index=False,
                             sheet_name="Resultados Completos")

    output.seek(0)  # Volver al inicio del archivo en memoria

    # Botón de descarga, visible todo el tiempo
    st.download_button(
        label="💾 Exportar resultados a Excel",
        data=output,
        file_name="resultados_prediccion.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
