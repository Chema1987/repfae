import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="REPFAE", layout="centered")

st.image("https://github.com/Chema1987/repfae/commit/fda71037d777aa402ba6e34e2bb3b61ac5615174", width=200)
st.title("Registro de Turnos - REPFAE")

# Inicializar sesión
if "datos" not in st.session_state:
    st.session_state["datos"] = []

# Formulario
with st.form("registro"):
    nombre = st.text_input("Nombre completo del estudiante", max_chars=100)
    correo = st.text_input("Correo UVa", max_chars=100)
    fecha = st.date_input("Fecha del turno")
    turno = st.selectbox("Tipo de turno", ["Mañana", "Tarde", "Noche", "Guardia"])
    profesor = st.text_input("Nombre completo del profesor")

    submitted = st.form_submit_button("Registrar turno")

    if submitted:
        if not nombre or not correo or not profesor:
            st.warning("Por favor, completa todos los campos.")
        else:
            horas = {"Mañana": 7.5, "Tarde": 7.5, "Noche": 10.5, "Guardia": 12}[turno]
            marcaje = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state["datos"].append({
                "Estudiante": nombre,
                "Correo UVa": correo,
                "Fecha": fecha.strftime("%Y-%m-%d"),
                "Turno": turno,
                "Horas": horas,
                "Profesor": profesor,
                "Marcaje": marcaje
            })
            st.success("Turno registrado correctamente.")

# Mostrar registros
if st.session_state["datos"]:
    df = pd.DataFrame(st.session_state["datos"])
    st.dataframe(df)

    # Exportar a Excel
    def generar_excel():
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name="Turnos")
            df.groupby("Estudiante")["Horas"].sum().reset_index().to_excel(writer, index=False, sheet_name="Resumen por Estudiante")
            df.groupby("Profesor")["Horas"].sum().reset_index().to_excel(writer, index=False, sheet_name="Resumen por Profesor")
        return output.getvalue()

    excel_data = generar_excel()
    st.download_button("📥 Descargar Excel", data=excel_data, file_name="REPFAE.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
