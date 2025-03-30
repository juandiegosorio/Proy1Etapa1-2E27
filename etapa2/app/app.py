import streamlit as st
import requests
import json

API_URL = "http://127.0.0.1:8000"  # Replace with your actual API URL if different
NUM_EXAMPLES = 10 # Default number of manual input fields

st.title('Detección de Noticias Falsas en Política')

option = st.sidebar.selectbox(
    '¿Qué deseas hacer hoy?',
    ('Predecir', 'Entrenar')
)

if option == 'Predecir':
    st.header('Predicción de Noticias Falsas')

    titulo = st.text_input("Título de la noticia:")
    descripcion = st.text_area("Descripción de la noticia:")
    fecha = st.date_input("Fecha de la noticia:")

    if st.button("Predecir"):
        if titulo and descripcion and fecha:
            payload = [
                {
                    "Titulo": titulo,
                    "Descripcion": descripcion,
                    "Fecha": str(fecha)
                }
            ]
            try:
                response = requests.post(f"{API_URL}/predict/", json=payload)
                response.raise_for_status()
                prediction_data = response.json()

                if "predictions" in prediction_data and prediction_data["predictions"]:
                    prediction = prediction_data["predictions"][0]
                    st.subheader("Resultado de la Predicción:")
                    st.write(f"**Título:** {prediction['Titulo']}")
                    st.write(f"**Descripción:** {prediction['Descripcion']}")
                    st.write(f"**Fecha:** {prediction['Fecha']}")
                    st.write(f"**Predicción:** {prediction['Prediccion']}")
                    st.write(f"**Probabilidad (Fake):** {prediction['Probabilidad']:.4f}")
                else:
                    st.error("No se recibieron predicciones válidas de la API.")

            except requests.exceptions.ConnectionError as e:
                st.error(f"Error de conexión con la API: {e}")
                st.info(f"Asegúrate de que la API esté corriendo en {API_URL}")
            except requests.exceptions.RequestException as e:
                st.error(f"Error al comunicarse con la API: {e}")
                try:
                    error_detail = response.json().get("detail")
                    if error_detail:
                        st.error(f"Detalle del error de la API: {error_detail}")
                except:
                    pass
        else:
            st.warning("Por favor, ingresa el título, la descripción y la fecha de la noticia.")

elif option == 'Entrenar':
    st.header('Entrenamiento del Modelo')

    training_option = st.radio(
        "¿Cómo prefieres proporcionar los datos de entrenamiento?",
        ("Ingresar manualmente", "Subir archivo JSON")
    )

    if training_option == "Ingresar manualmente":
        st.info(f"Por favor, ingresa la información de al menos {NUM_EXAMPLES} noticias para entrenar el modelo.")
        training_data = []
        labels = []
        for i in range(NUM_EXAMPLES):
            st.subheader(f"Ejemplo de Noticia {i + 1}")
            titulo = st.text_input(f"Título {i + 1}:", key=f"titulo_{i}")
            descripcion = st.text_area(f"Descripción {i + 1}:", key=f"descripcion_{i}")
            fecha = st.date_input(f"Fecha {i + 1}:", key=f"fecha_{i}")
            label = st.selectbox(f"Etiqueta {i + 1} (0: Real, 1: Fake):", [0, 1], key=f"label_{i}")
            training_data.append({"Titulo": titulo, "Descripcion": descripcion, "Fecha": str(fecha)})
            labels.append(label)

        if st.button("Entrenar Modelo con Datos Manuales"):
            # Basic check for non-empty data
            has_data = any(item["Titulo"] or item["Descripcion"] for item in training_data)
            if len(training_data) >= NUM_EXAMPLES and len(labels) >= NUM_EXAMPLES and has_data:
                payload = {"data": training_data, "labels": labels}
                try:
                    response = requests.post(f"{API_URL}/retrain/", json=payload)
                    response.raise_for_status()
                    metrics = response.json()
                    st.subheader("Resultados del Entrenamiento:")
                    st.success(metrics["message"])
                    st.write(f"**Precisión:** {metrics['precision']:.4f}")
                    st.write(f"**Recall:** {metrics['recall']:.4f}")
                    st.write(f"**F1-Score:** {metrics['f1_score']:.4f}")

                except requests.exceptions.ConnectionError as e:
                    st.error(f"Error de conexión con la API: {e}")
                    st.info(f"Asegúrate de que la API esté corriendo en {API_URL}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error al comunicarse con la API: {e}")
                    try:
                        error_detail = response.json().get("detail")
                        if error_detail:
                            st.error(f"Detalle del error de la API: {error_detail}")
                    except:
                        pass
            else:
                st.warning(f"Por favor, ingresa la información para al menos {NUM_EXAMPLES} ejemplos de noticias y sus etiquetas.")

    elif training_option == "Subir archivo JSON":
        st.info("Carga un archivo JSON con datos de entrenamiento en el formato: {'data': [...], 'labels': [...]}")
        uploaded_file = st.file_uploader("Cargar archivo JSON", type=["json"])

        if uploaded_file is not None:
            try:
                training_data = json.load(uploaded_file)
                data = training_data.get("data")
                labels = training_data.get("labels")

                if data and isinstance(data, list) and labels and isinstance(labels, list) and len(data) == len(labels) and len(data) >= 10:
                    if st.button("Entrenar Modelo con Archivo"):
                        payload = {"data": data, "labels": labels}
                        try:
                            response = requests.post(f"{API_URL}/retrain/", json=payload)
                            response.raise_for_status()
                            metrics = response.json()
                            st.subheader("Resultados del Entrenamiento:")
                            st.success(metrics["message"])
                            st.write(f"**Precisión:** {metrics['precision']:.4f}")
                            st.write(f"**Recall:** {metrics['recall']:.4f}")
                            st.write(f"**F1-Score:** {metrics['f1_score']:.4f}")

                        except requests.exceptions.ConnectionError as e:
                            st.error(f"Error de conexión con la API: {e}")
                            st.info(f"Asegúrate de que la API esté corriendo en {API_URL}")
                        except requests.exceptions.RequestException as e:
                            st.error(f"Error al comunicarse con la API: {e}")
                            try:
                                error_detail = response.json().get("detail")
                                if error_detail:
                                    st.error(f"Detalle del error de la API: {error_detail}")
                            except:
                                pass
                else:
                    st.error("El archivo JSON debe contener las claves 'data' (lista de noticias) y 'labels' (lista de enteros), con la misma longitud (mínimo 10), y en el formato esperado.")

            except json.JSONDecodeError:
                st.error("Error al decodificar el archivo JSON. Asegúrate de que el formato sea correcto.")
            except Exception as e:
                st.error(f"Ocurrió un error al cargar el archivo: {e}")