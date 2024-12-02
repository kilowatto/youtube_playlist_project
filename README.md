# YouTube Playlist Project

Este proyecto permite crear y gestionar automáticamente una playlist de YouTube utilizando la API de YouTube y un script en Python. El script autentica al usuario, busca canciones en YouTube y las añade a una playlist específica.

## Características

- Autenticación con OAuth 2.0 para acceso seguro a YouTube.
- Búsqueda y adición de canciones a una playlist existente o nueva.
- Uso de la cuota de la API de YouTube para administrar las solicitudes.
- Creación automática de una playlist de canciones navideñas.

## Requisitos

- Python 3.7 o superior.
- [YouTube Data API v3](https://developers.google.com/youtube/v3).
- Credenciales de API descargadas de Google Cloud (archivo `credentials.json`).
- Windows 10/11 con **Windows Subsystem for Linux (WSL)** habilitado.

## Instalación

### Instalación de WSL en Windows

Para ejecutar el script en un entorno similar a Linux desde Windows, necesitas instalar WSL. Aquí te mostramos cómo hacerlo:

1. **Abre PowerShell** como administrador (haz clic derecho en el botón de inicio de Windows y selecciona **Windows PowerShell (Admin)**).

2. **Ejecuta el siguiente comando para habilitar WSL**:

   ```powershell
   wsl --install
   ```

   Esto instalará la versión más reciente de Ubuntu en tu sistema.

3. **Reinicia tu computadora** para completar la instalación.

4. **Abre Ubuntu desde el menú de inicio** para terminar la configuración inicial de Linux (crea un usuario y una contraseña).

Para más información, visita [Microsoft WSL Documentation](https://docs.microsoft.com/es-es/windows/wsl/install).

### Instalación de Python y Dependencias

1. **Abre WSL (Ubuntu)** y asegúrate de tener Python instalado. Puedes instalar Python con el siguiente comando:

   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   ```

2. **Clona el repositorio del proyecto** en tu máquina:

   ```bash
   git repo clone kilowatto/youtube_playlist_project
   cd youtube_playlist_project
   ```

3. **Instala las dependencias necesarias** listadas en `requirements.txt`:

   ```bash
   pip3 install -r requirements.txt
   ```

### Configuración del Proyecto

1. **Credenciales de la API de YouTube**:

   - Crea un proyecto en [Google Cloud Console](https://console.developers.google.com/).
   - Habilita la **YouTube Data API v3**.
   - Descarga el archivo `credentials.json` y colócalo en la carpeta raíz del proyecto.

2. **Variables del Proyecto**:

   - **credentials.json**: Asegúrate de que este archivo esté en la misma carpeta donde ejecutas el script.
   - **songs\_list.csv**: Este archivo contiene la lista de canciones a añadir a la playlist. Puedes actualizar este archivo con nuevas canciones siguiendo el formato del CSV.

## Uso

Para ejecutar el script y crear o actualizar una playlist de YouTube, sigue estos pasos:

1. **Abre WSL (Ubuntu)** y navega a la carpeta del proyecto:

   ```bash
   cd /ruta/a/tu/proyecto/youtube_playlist_project
   ```

2. **Activa el entorno virtual** (opcional pero recomendado para aislar las dependencias):

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Ejecuta el script**:

   ```bash
   python3 create_playlist.py
   ```

   Esto abrirá un navegador para la autenticación con tu cuenta de Google. Después de la autenticación, el script buscará las canciones listadas en el archivo `songs_list.csv` y las añadirá a la playlist.

## Ejemplo de Uso

- El script solicitará autorización de acceso a YouTube. Abre el navegador y autoriza la aplicación.
- Una vez autenticado, el script comenzará a buscar y añadir canciones a la playlist.
- Si la cuota de la API se ha excedido, el script esperará automáticamente antes de intentarlo de nuevo.

## Notas Adicionales

- **Cuota de la API**: La YouTube Data API tiene un límite de cuota diario. Cada solicitud de búsqueda y de inserción consume parte de la cuota. Asegúrate de tener suficiente cuota antes de ejecutar el script.
- **Errores Comunes**:
  - Si ves el error de `quotaExceeded`, significa que se ha excedido la cuota diaria. El script está configurado para esperar antes de intentarlo de nuevo.

## Contribuciones

Si deseas contribuir a este proyecto, sigue estos pasos:

1. **Fork** el repositorio.
2. **Crea una rama** (`git checkout -b feature/nueva-caracteristica`).
3. **Commit tus cambios** (`git commit -m "Añadir nueva característica"`).
4. **Push a la rama** (`git push origin feature/nueva-característica`).
5. Abre un **Pull Request**.

## Licencia

Este proyecto está licenciado bajo la licencia MIT. Para más detalles, consulta el archivo `LICENSE`.

