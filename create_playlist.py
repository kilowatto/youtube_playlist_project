import os
import csv
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google_auth_oauthlib.flow import InstalledAppFlow
import webbrowser
import time
from datetime import datetime
from tqdm import tqdm
import platform
import subprocess
import ssl

# Define el archivo de secretos y los permisos que necesitas
CLIENT_SECRETS_FILE = "credentials.json"
SONG_LIST_CSV = "songs_list.csv"

# Parámetros de autenticación
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def clear_screen():
    """Limpiar la pantalla para una mejor presentación."""
    if os.name == 'nt':
        os.system('cls')  # Para Windows
    else:
        os.system('clear')  # Para Linux y MacOS

def authenticate():
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)

    try:
        # Intenta abrir el navegador en localhost automáticamente
        credentials = flow.run_local_server(port=34067)
    except Exception as e:
        print("No se pudo abrir el navegador automáticamente. Procederemos manualmente.")
        auth_url, _ = flow.authorization_url(prompt='consent')
        print(f"Por favor, visita la siguiente URL para autorizar la aplicación: {auth_url}")

        # Abrir el navegador, teniendo en cuenta si estamos en WSL
        try:
            if "microsoft-standard" in platform.uname().release:
                # WSL - abrir navegador de Windows utilizando xdg-open para mejor compatibilidad
                subprocess.run(['xdg-open', auth_url], check=True)
            else:
                # Otro entorno - intentar abrir el navegador estándar
                webbrowser.open(auth_url, new=1)
        except Exception as browser_error:
            print(f"No se pudo abrir el navegador automáticamente: {browser_error}")

        code = input("Introduce el código de autorización que obtuviste: ")
        flow.fetch_token(code=code)
        credentials = flow.credentials

    return credentials

def create_youtube_client(credentials):
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)
    return youtube

def check_quota(youtube, max_retries=3):
    """Comprueba la disponibilidad de la cuota con reintentos si hay problemas de SSL."""
    for attempt in range(max_retries):
        try:
            # Realizar una solicitud sencilla para comprobar la cuota
            request = youtube.search().list(part="snippet", q="test", maxResults=1)
            response = request.execute()
            print("Yuju! Tenemos cuota para avanzar.")
            return True
        except googleapiclient.errors.HttpError as e:
            if "quotaExceeded" in str(e):
                print("F**k, no podemos avanzar, tenemos que esperar.")
                return False
            else:
                raise
        except ssl.SSLEOFError as ssl_error:
            print(f"Problema SSL: {ssl_error}. Intento {attempt + 1} de {max_retries}. Esperando 5 segundos...")
            time.sleep(5)
        except Exception as e:
            print(f"Error inesperado: {e}. Intento {attempt + 1} de {max_retries}. Esperando 5 segundos...")
            time.sleep(5)

    # Si agotamos todos los intentos, devolvemos False
    print("Error SSL persistente después de varios intentos. No se pudo comprobar la cuota.")
    return False

def display_quota_info():
    # Como la API de YouTube no proporciona directamente la cuota restante,
    # aquí mostramos una información basada en la documentación conocida.
    print("\nInformación aproximada sobre el uso de la cuota:")
    print("- Límite de cuota diario: 10,000 unidades")
    print("- Unidades utilizadas por solicitud de búsqueda: 100")
    print("- Unidades utilizadas por inserción a la playlist: 50")
    print("- Nota: La cuota se renueva a la medianoche en la zona horaria del Pacífico (PST)\n")

def countdown(minutes):
    """Mostrar un contador hacia abajo en minutos y segundos."""
    for remaining_minutes in range(minutes, 0, -1):
        for remaining_seconds in range(59, -1, -1):
            time_left = f"Esperando {remaining_minutes - 1:02d} minutos y {remaining_seconds:02d} segundos para el siguiente intento."
            print(time_left, end='\r')
            time.sleep(1)
    print("Verificando cuota nuevamente...")

def get_or_create_playlist(youtube, title, description):
    # Buscar si la playlist ya existe
    request = youtube.playlists().list(
        part="snippet",
        maxResults=50,
        mine=True
    )
    response = request.execute()

    for item in response.get("items", []):
        if item["snippet"]["title"] == title:
            return item["id"]

    # Si no existe, crear una nueva
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["Christmas", "Holiday", "Music"],
                "defaultLanguage": "en"
            },
            "status": {
                "privacyStatus": "public"
            }
        }
    )
    response = request.execute()
    return response["id"]

def search_and_add_videos(youtube, playlist_id):
    # Leer el archivo CSV de canciones
    with open(SONG_LIST_CSV, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        song_list = list(reader)

    total_songs = len(song_list)
    successful_adds = 0
    quota_exceeded_count = 0

    # Barra de progreso para la lectura del archivo
    with tqdm(total=total_songs, desc="Leyendo canciones", position=0, leave=True) as pbar_read, \
         open(SONG_LIST_CSV, mode="w", newline="", encoding="utf-8") as file:

        fieldnames = ["Song Title", "Status", "YouTube Title", "YouTube URL", "Added At"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        # Iterar sobre cada canción del archivo
        for idx, song_row in enumerate(song_list):
            song = song_row["Song Title"]
            pbar_read.update(1)  # Actualizar la barra de progreso de lectura

            # Verificar si ya ha sido agregada
            if song_row.get("Status", "") == "Added":
                writer.writerow(song_row)
                continue

            try:
                # Buscar el video en YouTube
                request = youtube.search().list(
                    part="snippet",
                    maxResults=1,
                    q=song
                )
                response = request.execute()

                # Obtener el videoId del primer resultado
                if "items" in response and len(response["items"]) > 0:
                    video_id = response["items"][0]["id"]["videoId"]
                    video_title = response["items"][0]["snippet"]["title"]
                    video_url = f"https://www.youtube.com/watch?v={video_id}"

                    # Añadir el video a la playlist
                    add_video_request = youtube.playlistItems().insert(
                        part="snippet",
                        body={
                            "snippet": {
                                "playlistId": playlist_id,
                                "resourceId": {
                                    "kind": "youtube#video",
                                    "videoId": video_id
                                }
                            }
                        }
                    )
                    add_video_request.execute()

                    # Registro del éxito
                    successful_adds += 1
                    added_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    song_row.update({
                        "Status": "Added",
                        "YouTube Title": video_title,
                        "YouTube URL": video_url,
                        "Added At": added_at
                    })

                else:
                    song_row.update({"Status": "Not Found"})

            except googleapiclient.errors.HttpError as e:
                if "quotaExceeded" in str(e):
                    quota_exceeded_count += 1
                    print("F**k, no podemos avanzar, tenemos que esperar.")
                    song_row.update({"Status": "Quota Exceeded"})
                    writer.writerow(song_row)
                    continue

                song_row.update({"Status": f"Error: {str(e)}"})
                time.sleep(5)  # Espera antes de reintentar

            except Exception as e:
                song_row.update({"Status": f"Unexpected Error: {str(e)}"})

            # Escribir la canción (actualizada o no)
            writer.writerow(song_row)

        # Mensaje final con resultados y barras de progreso adicionales
        with tqdm(total=total_songs, desc="Canciones agregadas con éxito", position=1, leave=True) as pbar_success, \
             tqdm(total=total_songs, desc="Canciones no agregadas (cuota excedida)", position=2, leave=True) as pbar_fail:

            for song_row in song_list:
                if song_row.get("Status") == "Added":
                    pbar_success.update(1)
                elif song_row.get("Status") == "Quota Exceeded":
                    pbar_fail.update(1)

        print(f"Proceso completado. Canciones añadidas exitosamente: {successful_adds} de {total_songs}")

def main():
    # Limpiar la pantalla al inicio
    clear_screen()

    # Autenticación para obtener las credenciales
    credentials = authenticate()
    clear_screen()
    print("Autenticación completada exitosamente.")

    # Crear un cliente de YouTube con las credenciales
    youtube = create_youtube_client(credentials)

    # Mostrar información aproximada sobre la cuota
    display_quota_info()

    # Verificar si tenemos cuota disponible antes de continuar
    if not check_quota(youtube):
        print("Esperaremos 60 minutos antes de reintentar.")
        countdown(60)
        if not check_quota(youtube):
            print("No hay suficiente cuota. Terminando el proceso.")
            return

    # Definir el título y descripción de la playlist
    playlist_title = "Navidad 2024"
    playlist_description = "Playlist navideña con canciones en inglés y español, de diferentes artistas."
    
    # Obtener o crear la playlist
    playlist_id = get_or_create_playlist(youtube, playlist_title, playlist_description)
    print(f"Playlist creada/existente con ID: {playlist_id}")
    
    # Añadir canciones a la playlist
    search_and_add_videos(youtube, playlist_id)

if __name__ == "__main__":
    main()
