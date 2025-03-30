# Detección de Noticias Falsas en Política (Colombia)
## Elaborado por: 
Juan Manuel Ramirez

Daniel Esteban Gomez

Juan Diego Osorio

Este proyecto consta de una API construida con FastAPI para la detección de noticias falsas en el ámbito político colombiano y una aplicación web Streamlit para interactuar con dicha API.

## Cómo Correr la API (Carpeta `api`)

Sigue estos pasos para iniciar el servidor de la API FastAPI:

1.  **Navega al directorio de la API:**
    Abre tu terminal o símbolo del sistema y cambia al directorio `api` dentro de la raíz del proyecto:

    ```bash
    cd api
    ```

2.  **Crea un entorno virtual (recomendado):**
    Si no tienes un entorno virtual activado, es una buena práctica crear uno para aislar las dependencias del proyecto:

    ```bash
    python -m venv venv
    source venv/bin/activate  # En Linux/macOS
    venv\Scripts\activate  # En Windows
    ```

3.  **Instala las dependencias de la API:**
    Asegúrate de tener instalado `pip` y luego instala las librerías necesarias listadas en el `requirements.txt` (que debe estar en la raíz del proyecto). Puedes copiar el `requirements.txt` a la carpeta `api` o ejecutar el comando desde la raíz:

    ```bash
    pip install -r ../requirements.txt
    ```

4.  **Ejecuta la API con Uvicorn:**
    Utiliza el siguiente comando para iniciar el servidor FastAPI:

    ```bash
    uvicorn app:app --reload
    ```

    * `uvicorn`: El servidor ASGI.
    * `app:app`: Especifica el módulo `app.py` y la instancia de la aplicación FastAPI llamada `app`.
    * `--reload`: Activa la recarga automática del servidor al detectar cambios en el código (útil para desarrollo).

5.  **Accede a la API:**
    Una vez que el servidor se inicie, podrás acceder a la API en tu navegador o con herramientas como `curl` o Postman, generalmente en la dirección `http://127.0.0.1:8000`. Puedes probar el endpoint raíz accediendo a esa dirección.

## Cómo Correr la Aplicación Streamlit (Carpeta `app`)

Sigue estos pasos para iniciar la interfaz de usuario Streamlit:

1.  **Navega al directorio de la aplicación:**
    Abre una **nueva** terminal o símbolo del sistema (mantén la API corriendo en la otra) y cambia al directorio `app` dentro de la raíz del proyecto:

    ```bash
    cd app
    ```

2.  **Activa el entorno virtual (si lo creaste):**
    Si creaste y activaste un entorno virtual para la API, asegúrate de activarlo también en esta nueva terminal:

    ```bash
    source ../venv/bin/activate  # En Linux/macOS
    ..\venv\Scripts\activate  # En Windows
    ```

3.  **Instala las dependencias de la aplicación (si no lo hiciste antes):**
    Si no instalaste las dependencias desde la raíz del proyecto, puedes hacerlo ahora (asegurándote de que `streamlit` esté incluido en tu `requirements.txt`):

    ```bash
    pip install -r ../requirements.txt
    ```

4.  **Ejecuta la aplicación Streamlit:**
    Utiliza el siguiente comando para iniciar la aplicación web:

    ```bash
    streamlit run streamlit_app.py
    ```

    Esto abrirá automáticamente una nueva pestaña en tu navegador con la interfaz de la aplicación Streamlit.

## Uso de la Aplicación Streamlit

Una vez que la aplicación Streamlit esté corriendo en tu navegador, podrás interactuar con las siguientes funcionalidades:

* **Predecir:** Ingresa el título, la descripción y la fecha de una noticia política para obtener una predicción sobre si es falsa o real, junto con una probabilidad. La aplicación enviará esta información a la API para obtener el resultado.

* **Entrenar:**
    * **Ingresar manualmente:** Completa los formularios con la información de al menos 5 noticias (título, descripción, fecha y etiqueta: 0 para Real, 1 para Fake). Haz clic en "Entrenar Modelo con Datos Manuales" para enviar estos datos a la API y reentrenar el modelo.
    * **Subir archivo JSON:** Carga un archivo JSON con datos de entrenamiento en el formato `{"data": [{"Titulo": ..., "Descripcion": ..., "Fecha": ...}, ...], "labels": [0, 1, ...]}`. Haz clic en "Entrenar Modelo con Archivo" para enviar los datos a la API y reentrenar el modelo.

**¡Importante!** Asegúrate de que la API esté corriendo en segundo plano antes de intentar usar la aplicación Streamlit, ya que la aplicación se comunica con la API para realizar las predicciones y el reentrenamiento.