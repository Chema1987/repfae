import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="REPFAE - Registro de Turnos", layout="wide")

st.title("📚 REPFAE - Registro de Turnos de Prácticas")

# Inicializar estado
if "turnos" not in st.session_state:
    st.session_state["turnos"] = []

# Geolocalización
st.subheader("Marcaje de Turno")

nombre = st.text_input("Nombre completo del estudiante")
correo = st.text_input("Correo UVa")
fecha = st.date_input("Fecha del turno", value=datetime.now())
turno = st.selectbox("Tipo de turno", ["Mañana", "Tarde", "Noche", "Guardia"])
profesor = st.text_input("Nombre completo del profesor responsable")

st.write("Activa tu geolocalización para poder registrar el turno.")
loc_data = st_folium(folium.Map(location=[40.4168, -3.7038], zoom_start=6), width=700, height=500)

registrar = st.button("Registrar turno")

if registrar:
    if not nombre or not correo or not profesor:
        st.error("⚠️ Todos los campos son obligatorios.")
    elif loc_data["last_clicked"] is None:
        st.error("⚠️ Debes marcar tu ubicación en el mapa para registrar el turno.")
    else:
        # Cálculo de horas por tipo de turno
        horas_dict = {"Mañana": 7.5, "Tarde": 7.5, "Noche": 10.5, "Guardia": 12}
        horas = horas_dict[turno]
        marcaje = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lat = loc_data["last_clicked"]["lat"]
        lon = loc_data["last_clicked"]["lng"]
        st.session_state["turnos"].append({
            "Estudiante": nombre,
            "Correo UVa": correo,
            "Fecha": fecha.strftime("%Y-%m-%d"),
            "Turno": turno,
            "Horas": horas,
            "Profesor": profesor,
            "Marcaje": marcaje,
            "Latitud": lat,
            "Longitud": lon
        })
        st.success("✅ Turno registrado correctamente.")

# Mostrar turnos registrados
if st.session_state["turnos"]:
    df = pd.DataFrame(st.session_state["turnos"])
    st.subheader("📄 Turnos Registrados")
    st.dataframe(df)

    # Crear mapa de estudiantes
    st.subheader("🗺️ Mapa de Localización de Turnos")
    m = folium.Map(location=[40.4168, -3.7038], zoom_start=6)

    color_dict = {"Mañana": "green", "Tarde": "orange", "Noche": "blue", "Guardia": "red"}
    for _, row in df.iterrows():
        folium.Marker(
            location=[row["Latitud"], row["Longitud"]],
            popup=f"{row['Estudiante']} - {row['Turno']} - {row['Marcaje']}",
            icon=folium.Icon(color=color_dict.get(row["Turno"], "gray"))
        ).add_to(m)

    st_folium(m, width=700, height=500)

    # Botón para descargar Excel
    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Turnos")
            df.groupby("Estudiante")["Horas"].sum().reset_index().to_excel(writer, index=False, sheet_name="Resumen_Estudiantes")
            df.groupby("Profesor")["Horas"].sum().reset_index().to_excel(writer, index=False, sheet_name="Resumen_Profesores")
        return output.getvalue()

    excel_data = to_excel(df)
    st.download_button("📥 Descargar Excel con Resumen", data=excel_data, file_name="Registro_REPFAE.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
