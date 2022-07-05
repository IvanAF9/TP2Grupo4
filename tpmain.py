import tekore as tk
from tekore import RefreshingToken, Spotify
import os
import pickle
import csv
import time
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from lyricsgenius import Genius
from wordcloud import WordCloud, STOPWORDS 
import matplotlib.pyplot as plt #para mostrar nuestra nube de palabras
from PIL import Image #para cargar nuestra imagen
import numpy as np #para obtener el color de nuestra imagen

def acceso_youtube():
    '''Genera conexion con youtube a traves de la clave.json
        PRE: No recibe nada
        POS: Devuelve la conexion del tipo "Service_youtube" con la API'''
    credentials = None
    # ver que las credenciales sigan siendo validas o crearlas
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:  
            credentials = pickle.load(token)
    try:
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                print("Refrescando token de acceso...")
                credentials.refresh(Request())
            else:
                print("Esperando autorizacion...")
                print()
                flow = InstalledAppFlow.from_client_secrets_file("clave.json",
                                                                 scopes=["https://www.googleapis.com/auth/youtube"])

                flow.run_local_server(port=8080, prompt="consent",
                                      authorization_prompt_message="")  # prompt es para recibir el token de actualizacion
                credentials = flow.credentials

                # Guardar las credenciales en un archivo pickle
                with open("token.pickle", "wb") as f:
                    print("Inicio de sesion exitoso")
                    pickle.dump(credentials, f)

        service_youtube = build("youtube", "v3", credentials=credentials)
        return service_youtube

    except:
        print("Ha ocurrido un error, pruebe con la opcion 3 del menu: Administrar cuenta de Youtube ")

        return None

def channel_request(service_youtube) -> str:
    """Obtiene el nombre del canal de la sesion actual para youtube"""
    """ PRE: recibe la conexion del tipo "Service_youtube" con la API
        POS: devuelve el nombre del canal de youtube """
    canal = service_youtube.channels().list(part="snippet", mine=True).execute()
    nombre_canal = canal["items"][0]["snippet"]["title"]
    return nombre_canal

def acceso_spotify() -> Spotify:
    '''Genera conexion con spotify a traves del id_cliente y cliente_secreto
        PRE: No recibe nada
        POS: Devuelve la conexion del tipo "Spotify" con la API'''

    print('\nEstá a punto de ser enviado a Spotify para pedir autorización a su cuenta.')
    print(
        f'Luego de eso será redireccionado a otra pagina y el programa le pedirá que copie el link al que fue redireccionado.')
    input_usuario = input('Presione ENTER para continuar: \n')
    id_cliente = '4e1bc2b1c16e4005b0b53b549ee818d4'
    cliente_secreto = '27e3e8415ef44fe997e731d830ec5541'
    redireccion_uri = 'https://github.com/IvanAF9/TP2Grupo4'
    conf = (id_cliente, cliente_secreto, redireccion_uri)
    try:
        token_usuario = tk.prompt_for_user_token(*conf,
                                             scope=tk.scope.every)  # pide permisos al usuario y redirecciona, devuelve token
        return tk.Spotify(token_usuario)  # Inicia la conexion a la API Spotify
    except:
        print('Error: URL incorrecta')
    
def listar_playlists(spotify: Spotify, solo_mostrar_titulo_playlist: str):
    '''Hace un print de las playlists del usuario actual por cancion y artista
	PRE: Recibe la conexion del tipo "Spotify" con la API
	POS: Devuelve playlist elegida por usuario solamente si solo_mostrar_titulo_playlist es igual a "si" '''
    lista_playlists_titulos: list = []
    usuario = spotify.current_user()  # obtiene datos del usuario logueado
    playlists = spotify.playlists(usuario.id)
    cantidad_playlists: int = 0
    for playlist_usuario in playlists.items:
        playlist_actual = spotify.playlist(playlist_usuario.id)
        if solo_mostrar_titulo_playlist == 'no':
            print(f'\n ***** Playlist: {playlist_usuario.name} *****\n')
            lista_artistas = []
            for cancion in playlist_actual.tracks.items:
                lista_artistas = []
                nombre_cancion = cancion.track.name
                print(f'Cancion: {nombre_cancion}')
                if hasattr(cancion.track,
                           'artists'):  # comprueba si el objecto cancion.track contiene el atributo artists, ya que si no devuelve error
                    for artista in cancion.track.artists:
                        lista_artistas.append(artista.name)
                if lista_artistas != []:
                    artistas_string = ' - '.join(lista_artistas)
                    print(f'Artistas: {artistas_string}')
        else:
            cantidad_playlists += 1
            if cantidad_playlists == 1:
                print('\nPlaylists actuales:')
            print(f'{cantidad_playlists}- {playlist_usuario.name}')
            lista_playlists_titulos.append(playlist_usuario)
    if solo_mostrar_titulo_playlist == 'si':
        eleccion_playlist = input('Cual playlist elige? Escriba el numero 1,2,3,etc: ')

        chequeo_opcion = 0
        while chequeo_opcion == 0:
            try:
                lista_playlists_titulos[int(eleccion_playlist) - 1]
            except:
                eleccion_playlist = input('Eleccion incorrecta, cual playlist elige? Escriba el numero 1,2,3,etc: ')
            else:
                chequeo_opcion = 1
        return lista_playlists_titulos[int(eleccion_playlist) - 1]

def mostrar_letra_cancion(usuario_eleccion_elemento, genius: Genius):
    '''Busca y muestra letra de canciones buscadas por el usuario
    PRE: Recibe el objeto usuario_eleccion_elemento con informacion de la cancion buscada y la conexion a la API de Genius
    POS: No devuelve nada
    '''
    cancion = genius.search_song(usuario_eleccion_elemento.name, usuario_eleccion_elemento.artists[0].name)
    print(f'\n{cancion.lyrics}')

def autorizacion_lyrics_genius()->Genius:
    '''Sirve para devolver la conexion a la API de Genius
    PRE: Contiene la informacion de id_client, cliente_secreto y token de acceso
    POS: Devuelve la conexion del tipo Genius a su API
    '''
    id_cliente = 'piIkU0vJQShzcYoRAShmPcpyzZvgNHHKJVtMhyGh1Knddp2PNs-KITMBD2n9k5xh'
    cliente_secreto = 'jRZMg5zpmYbrXIxyN4KiNWGc84pW-J7pRLdd4E5t4feebqUlejrUNpwnQ3OVKc1H7QWOmeKyc_Xl_q-UirucMw'
    token_acceso_cliente = 'EHppP0Vw_U0Q7GkQIheMi_G-hWDr794lSPuiPc_4WTktXPfd0gkXe_fXznGM424j'
    genius = Genius(token_acceso_cliente)

    return genius

def agregar_elemento_en_playlist(spotify: Spotify, usuario_eleccion_elemento):
    '''Agrega elementos encontrados a una playlist a eleccion
    PRE: Recibe la conexion del tipo "Spotify" con la API y el elemento elegido por el usuario
    POS: No devuelve nada, modifica la playlist en spotify
    '''
    playlist_elegida = listar_playlists(spotify, 'si')
    spotify.playlist_add(playlist_elegida.id, [usuario_eleccion_elemento.uri])
    print('\n*** ¡Elemento agregado a la playlist! ***')

def accion_con_elementos_buscados(spotify: Spotify, usuario_eleccion_elemento):
    '''Consulta al usuario que hacer con elementos que se encuentran en una busqueda
    	PRE: Recibe la conexion del tipo "Spotify" con la API, el tipo de elemento buscado (con sus atributos) y la lista de elementos encontrados
    	POS: No devuelve nada, se va a mostrar_letra_cancion() o hacia agregar_elemento_en_playlist()'''
    opcion: int = 1
    while opcion == 1:
        print('\nDesea hacer algo con uno de los elementos encontrados?')
        print('1- Agregarlo a una playlist existente')
        print('2- Mostrar su letra (solo con canciones)')
        print('3- Volver al MENU')
        pregunta_usuario = input('\nElija 1, 2, 3: ')
        while pregunta_usuario not in ('1', '2', '3'):
            pregunta_usuario = input('Incorrecto, elija 1, 2, 3: ')

        if pregunta_usuario == '1':
            agregar_elemento_en_playlist(spotify, usuario_eleccion_elemento)
        elif pregunta_usuario == '2':
            if usuario_eleccion_elemento.type == 'track':
                genius = autorizacion_lyrics_genius()
                mostrar_letra_cancion(usuario_eleccion_elemento, genius)
            else:
                print('\nSolo se puede mostrar letra de canciones, y el elemento encontrado no lo es.')
        else:
            opcion = 0

def buscador_spotify(spotify: Spotify):
    '''Permite al usuario hacer una busqueda
	PRE: Recibe la conexion del tipo "Spotify" con la API
	POS: No devuelve nada, si el usuario elige usar alguno de los elementos se va a accion_con_elementos_buscados()'''
    nombre_elementos_lista: list = ['artist', 'album', 'episode', 'playlist', 'show', 'track']
    print('\nQue clase de elemento quiere buscar?')
    print('1- Artista\n2- Album\n3- Episodio\n4- Playlist\n5- Show\n6- Cancion\n')
    usuario_eleccion_elemento = input('Elija escribiendo el numero (1,2,3,etc): ')
    while usuario_eleccion_elemento not in ('1', '2', '3', '4', '5', '6'):
        usuario_eleccion_elemento = input('Incorrecto, elija una opcion con el numero que corresponda: ')

    usuario_eleccion_elemento = nombre_elementos_lista[int(usuario_eleccion_elemento) - 1]

    usuario_busca: str = input('\nEscriba lo que quiere buscar: ')

    listado_elementos_encontrados: list = []  # lista de elementos encontrados
    for elementos in spotify.search(usuario_busca, types=(usuario_eleccion_elemento,)):
        for usuario_eleccion_elemento in elementos.items:  # recorre cada elemento encontrado
            if len(listado_elementos_encontrados) < 3:
                listado_elementos_encontrados.append(usuario_eleccion_elemento)

    # Muestra los 3 elementos encontrados mas populares
    if len(listado_elementos_encontrados) > 0:
        print('\nLas opciones mas reproducidas de mayor a menor son:')

        if len(listado_elementos_encontrados) > 3:
            for i in range(3):
                lista_artistas = []
                for artista in listado_elementos_encontrados[i].artists:
                    lista_artistas.append(artista.name)
                artistas_string = ' - '.join(lista_artistas)

                print(f'{i + 1}: {listado_elementos_encontrados[i].name}. Artista/s: {artistas_string}')
        else:
            for i in range(len(listado_elementos_encontrados)):
                lista_artistas = []
                for artista in listado_elementos_encontrados[i].artists:
                    lista_artistas.append(artista.name)
                artistas_string = ' - '.join(lista_artistas)

                print(f'{i + 1}: {listado_elementos_encontrados[i].name}. Artista/s: {artistas_string}')

        pregunta_usuario = input('\nQuiere usar alguno de los elementos? si/no ').lower()
        while pregunta_usuario not in ('si', 'no'):
            pregunta_usuario = input('Incorrecto, escriba si o no: ').lower()
        if pregunta_usuario == 'si':
            usuario_elige = input('Cual elemento desea usuar? Elija 1,2,3,etc: ')
            chequeo_opcion = 0
            while chequeo_opcion == 0:
                try:
                    listado_elementos_encontrados[int(usuario_elige) - 1]
                except:
                    usuario_elige = input('Incorrecto, cual elemento desea usuar? Elija 1,2,3,etc: ')
                else:
                    chequeo_opcion = 1

            accion_con_elementos_buscados(spotify, listado_elementos_encontrados[int(usuario_elige) - 1])
        
    else:
        print('\nNo se ha encontrado resultados para su busqueda')

def crear_playlist_spotify(spotify: Spotify):
    '''Crea nueva playlist vacia para el usuario actual
    PRE: Recibe la conexion con la API spotify
    POS: No devuelve nada'''
    usuario_actual = spotify.current_user()
    nombre_playlist_nueva = input('\nEscriba el nombre de la nueva playlist a crear: ')
    spotify.playlist_create(usuario_actual.id, nombre_playlist_nueva)
    print('\n*** Playlist creada con EXITO ***\nPara agregarle canciones, '
          'vaya al menu principal y use el buscador de Spotify para hacerlo')
	
def listar_playlists_youtube(service_youtube) -> list:
    """ PRE: recibe la conexion del tipo "Service_youtube" con la API
        POS: devuelve una lista de diccionarios con el id y el titulo de las listas de reproduccion"""
    requests = service_youtube.playlists().list(part="contentDetails, snippet", mine=True, maxResults=50)
    response = requests.execute()
    list_items = response["items"]
    lista_aux: list = list()

    for i in range(len(list_items)):
        dicc_aux = {
            "playlistId": list_items[i]["id"],
            "title": list_items[i]["snippet"]["title"]
        }
        lista_aux.append(dicc_aux)

    return lista_aux

def validar_ingreso_int(texto: str) -> int:
    """Verifica que la entrada por parte del usuario sea un entero"""
    """ PRE: recibe un string
        POS: devuelve un entero"""
    select = input(texto)
    es_numerico = select.isnumeric()

    while es_numerico != True:
        print("Opcion invalida")
        select = input(texto)
        es_numerico = select.isnumeric()

    select = int(select)

    return select

def sub_menu_acceso_youtube() -> tuple:
    """ PRE: no recibe nada
        POS: devuelve una tupla con la conexion del tipo "Service_youtube" con la API 
        y la confirmacion del inicio de sesion en youtube"""
    service_youtube = None
    sesion_iniciada = False
    print()
    print("Administrar cuenta de Youtube:")
    opciones: list = [
        "1 - Iniciar sesion",
        "2 - Ver usuario actual",
        "3 - Cambiar usuario",
        "4 - Volver al menu"
    ]
    for i in range(len(opciones)):
        print(opciones[i])
    texto = "Ingrese una opcion: "
    select = validar_ingreso_int(texto)
    while select != 4:
        if select not in [1,2,3]:
            print("Opcion invalida")
            select = validar_ingreso_int(texto)
        else: 
            if select == 1:
                print()
                service_youtube = acceso_youtube()
                print("Sesion iniciada")
                sesion_iniciada = True

            elif select == 2:
                print()
                if os.path.exists("token.pickle"):
                    service_youtube = acceso_youtube()
                    nombre_canal = channel_request(service_youtube)
                    print("Usuario actual:", nombre_canal)
                    sesion_iniciada = True
                    # hacer request para obtener el id del canal y asociarlo a la lista_usuario
                    # imprimir el nombre
                else:
                    print("No existe usuario actual")
            elif select == 3:
                print()
                if os.path.exists("token.pickle"):
                    os.remove("token.pickle")
                    service_youtube = acceso_youtube()
                    sesion_iniciada = True
                else:
                    print("No existe usuario, por favor inicie sesion")
            print()
            print("Administrar cuenta de Youtube:")
            for i in range(len(opciones)):
                print(opciones[i])
            select = validar_ingreso_int(texto)

    return service_youtube, sesion_iniciada

def mostrar_playlist_youtube(service_youtube) -> list:
    """ PRE: recibe la conexion del tipo "Service_youtube" con la API
        POS: retorna una lista con el titulo de todas las playlist del canal de youtube"""
    lista_playlist = listar_playlists_youtube(service_youtube)
    lista_playlist.append({"title":"Volver al menu"})
    i: int = 0
    print()
    print("Playlist:")
    for lista in lista_playlist:
        i+=1
        if i<len(lista_playlist):
            print(i,"- ***",lista["title"],"***")
        else:
            print(i,"-",lista["title"])
    return lista_playlist

def mostrar_canciones_playlist_youtube(
        service_youtube,select: int, lista_playlist: list) -> list:
    """ PRE: recibe la conexion del tipo "Service_youtube" con la API,
        un entero y la lista de titulos de las playlist de youtube
        POS: devuelve una lista con el titulo de las canciones o videos pertenecientes a la playlist
        elegida con el entero """
    print("Cargando canciones...")
    lista_canciones: list = list()
    playlist = service_youtube.playlistItems().list(
        part='snippet',
        playlistId=lista_playlist[select-1]["playlistId"],
        maxResults=50
    )
            
    playlist = playlist.execute()
    print()

    if len(playlist["items"])==0:
            print("No hay canciones en esta playlist")
    else:
        print("Playlist:",lista_playlist[select-1]["title"])
        print("Canciones:")
        for item in playlist['items']:
                print('-', item['snippet']['title'])
                lista_canciones.append(item['snippet']['title'])
    print()
    return lista_canciones

def listar_playlist_y_temas_youtube(service_youtube) -> None:
    """Hace un print con todas las playlist del canal y las canciones por playlist"""
    """ PRE: recibe la conexion del tipo "Service_youtube" con la API
        POS: no devuelve nada""" 
    print("Cargardo listas...")
    try:
        lista_playlist = mostrar_playlist_youtube(service_youtube)
        texto: str = "Seleccione el nro de lista para ver las canciones en ella o vuelva al menu: "
        select = validar_ingreso_int(texto)
        while select != len(lista_playlist):
            if select<1 or select>len(lista_playlist):
                print("Opcion invalida")
                select = validar_ingreso_int(texto)
            else:
                lista_canciones = mostrar_canciones_playlist_youtube(service_youtube,select,lista_playlist)
                lista_playlist = mostrar_playlist_youtube(service_youtube)
                select = validar_ingreso_int(texto)
    except:
        print("Ha ocurrido un error, por favor intentelo de nuevo")

def ver_todos_los_temas_youtube(service_youtube) -> list:
    """ PRE: recibe la conexion del tipo "Service_youtube" con la API
        POS: devuelve una lista de diccionarios con el id y el titulo de todos los videos 
        o caciones pertencientes a todas las playlist del canal de youtube"""
    lista_playlist = listar_playlists_youtube(service_youtube)
    lista_aux: list = list()
    dicc_aux: dict = dict()
    for i in range(len(lista_playlist)):
        playlist = service_youtube.playlistItems().list(
            part='snippet',
            playlistId=lista_playlist[i]["playlistId"],
            maxResults=50
        )

        playlist = playlist.execute()
        for item in playlist['items']:
            dicc_aux = {
                "title": item['snippet']['title'],
                "videoid": item["snippet"]["resourceId"]["videoId"]
            }
            lista_aux.append(dicc_aux)

        for i in range(len(lista_aux)):
            for j in range(len(lista_aux)):
                if i != j and i < len(lista_aux) and j < len(lista_aux):
                    if lista_aux[i]["videoid"] == lista_aux[j]["videoid"]:
                        lista_aux.remove(lista_aux[j])

    return lista_aux

def crear_playlist_youtube(service_youtube, nueva_lista: str) ->None:
    """Crea una playlist en el canal de youtube"""
    """ PRE: recibe la conexion del tipo "Service_youtube" con la API y un nombre
        POS: no devuelve nada"""
    playlists_insert_response = service_youtube.playlists().insert(
        part="snippet,status",
        body=dict(
            snippet=dict(
                title=nueva_lista,
                description="A private playlist created with the YouTube API v3"
            ),
            status=dict(
                privacyStatus="private"
            )
        )
    ).execute()

def insertar_en_playlist_youtube(
        service_youtube, ultima_playlistId: str, videoId: str) -> None:
    """Inserta elementos en una playlist"""
    """ PRE: recibe la conexion del tipo "Service_youtube" con la API, 
        el id la playlist y el id del video a insertar en esta
        POS: no devuelve nada"""
    insertar_tema = service_youtube.playlistItems().insert(
                part='snippet',
                body={
                    "snippet":{
                        "playlistId":ultima_playlistId,
                        "resourceId":{
                            "kind":"youtube#video",
                            "videoId":videoId
                        }
                    }
                }
    ).execute()

def crear_lista_de_reproduccion_youtube(service_youtube) -> None:
    """Invoca las funciones necesarias para crear una playlist y agregarle canciones o videos"""
    """ PRE: recibe la conexion del tipo "Service_youtube" con la API, 
        POS: no devulve nada"""
    nueva_lista: str = input("Ingrese el nombre de la lista a crear: ")
    no_valido: bool = True
    while no_valido == True:
        todos_espacios: int = 0
        for caracter in nueva_lista:
            if caracter == " ":
                todos_espacios += 1
        if todos_espacios == len(nueva_lista):
            no_valido =True
            nueva_lista = input("Ingrese un nombre para la lista: ")
        else:
            no_valido = False
    print("Creando lista de reproduccion...")
    crear_playlist_youtube(service_youtube, nueva_lista)
    print("Lista creada")
    print("Cargando canciones...")
    time.sleep(1) #darle tiempo al servidor para que al llamar nuevamente a las listas, incluya la ultima creada
    lista_playlist = listar_playlists_youtube(service_youtube)
    ultima_playlistId = lista_playlist[0]["playlistId"]
    lista_temas = ver_todos_los_temas_youtube(service_youtube)
    lista_temas.append({"title":"Volver al menu"})
    i: int = 0
    print()
    print("Canciones existentes en todas sus playlist:")
    for lista in lista_temas:
        i+=1
        if i<len(lista_temas):
            print(i,"- ***",lista["title"],"***")
        else:
            print(i,"-",lista["title"])
    texto: str = "Seleccion una cancion para listar en la playlist creada o vuelva al menu: "
    select = validar_ingreso_int(texto)
    while select != len(lista_temas):
        if select<1 or select>len(lista_temas):
            print("Opcion invalida")
        else:
            videoId = lista_temas[select-1]["videoid"]
            print("Listando cancion...")
            insertar_en_playlist_youtube(service_youtube, ultima_playlistId, videoId)
            lista_temas.remove(lista_temas[select-1])
            print("Elemento listado")
            print()
            print("Elementos restantes:")
            i = 0
            for lista in lista_temas:
                i+=1
                if i<len(lista_temas):
                    print(i,"- ***",lista["title"],"***")
                else:
                    print(i,"-",lista["title"])
        select = validar_ingreso_int(texto)

def expotar_playlist_youtube(service_youtube):
    '''pre:recibe las credenciales
       pos:exportar una playlist y sus videos a
       un archivo csv
    '''
    lista_playlist = listar_playlists_youtube(service_youtube)
    contador = 0

    for lista in lista_playlist:
        contador += 1
        print(contador, lista["title"])

    numero_playlist = int(input('Ingrese el numero de la playlist que desea exportar: '))
    id = lista_playlist[numero_playlist - 1]["playlistId"]

    playlist = service_youtube.playlistItems().list(
        part='snippet',
        playlistId=id,
        maxResults=50
    )
    playlist = playlist.execute()
    nombre_videos = []

    for item in playlist['items']:
        nombres = item['snippet']['title']
        nombre_videos.append(nombres)
        descripcion = item['snippet']['description']
        titulo = item['snippet']['title']
        channel_id = item['snippet']['channelId']
        time = item['snippet']['publishedAt']

    nombre_playlist = ('-Titulo de la playlist: : ', titulo)
    atributos = ('-Id del canal: ', channel_id, '-Tiempo de subida: ', time)
    descripcion_general = ('-Descripcion general: ', descripcion)

    try:
        with open('archivo_playlists.csv', 'w', newline='') as lista:
            datos = csv.writer(lista, delimiter=' ')
            datos.writerow(nombre_playlist)
            datos.writerows(nombre_videos)
            datos.writerow(atributos)
            datos.writerow(descripcion_general)
    except UnicodeEncodeError:
        print('Hubo un error con la descipcion, por un caracter no aceptado')
    except:
        print("Error con la apertura del archivo")

def mostrar_lyric(cancion: str):
    token_genius = "hzZzDlh8ecFwCdcMsyVeCCdC_PH62cDSEJgIPXTn2JSq1qlHnn2GcqvsZyN0p-9o"
    '''Este token fue generado a partir de la cuenta mail del loco mauro.'''
    genius = Genius(token_genius)

    if ("Official Video" in cancion 
        or "Live" in cancion
        or "Video Oficial" in cancion):
        cancion = cancion.replace("(Official Video)", "")
        cancion = cancion.replace("(Live)", "")
        cancion = cancion.replace("(Video Oficial)", "")

    song = genius.search_song(cancion)
    if(song == None):
        song = ""
    else:
        song = str(song)
    return song


def buscador_youtube(youtube) -> None:
    print("Buscador de YouTube. Que desea ver?")
    print("\nEscriba lo que quiera buscar (nombre de video, nombre de canal, cantante, etc)")
    busqueda: str = input("-- ")
    while (busqueda == ""):
        busqueda = input("No puede buscar algo vacío: ")
    y: int = -1
    search_in_youtube = youtube.search().list(
        q=busqueda,
        order="viewCount",
        part="id, snippet",
        maxResults=3
    ).execute()
    videos: list = []
    print('Buscando videos...')

    if (search_in_youtube["items"] == []):
        print("\n No se encontraron resultados.")
    else:
        print("\nLos videos que se encontraron son (según reproducciones): ")
        for resultado in search_in_youtube.get("items", []):
            y += 1
            if resultado["id"]["kind"] == "youtube#video":
                videos.append("%s (%s)" % (resultado["snippet"]["title"],
                                           resultado["id"]["videoId"]))
            print(f"\n{y + 1}- {videos[y][0: len(videos[y]) - 13]}")
        print("\nDesea agregar alguna de las opciones a una playlist? (1 = Sí / ENTER = No)")
        decision: str = input("Respuesta: ")

        while (decision == '1' and len(videos) <= 3 and len(videos) != 0):
            i: int = 0
            list_video: list = []

            for v in videos:
                i += 1
                print(f'\n{i} - {v[0: len(v) - 13]}')
                list_video.append([i, v])
            video_elegido: str = input("\nCual elemento va a agregar (1, 2, 3): ")

            while (video_elegido != '1' and
                   video_elegido != '2' and
                   video_elegido != '3'):
                video_elegido = input('\nElija un video: ')

            elegido = list_video[int(video_elegido) - 1][1]
            videoId = elegido[len(elegido) - 12: len(elegido) - 1]
            print("\nLas playlist disponibles son: ")
            todas_las_playlist = listar_playlists_youtube(youtube)
            i = 0

            for playlist in todas_las_playlist:
                i += 1
                print(f"{i} - {playlist['title']}")

            print("\nA cuál lista lo queres agregar?: ")
            playlist_elegida: str = input("\nPlaylist elegida: ")
            num_playlist: int = int(playlist_elegida)

            while (num_playlist > len(todas_las_playlist)):
                playlist_elegida = input("Playlist elegida: ")
                num_playlist: int = int(playlist_elegida)

            playlistId = todas_las_playlist[int(playlist_elegida) - 1]['playlistId']
            print("Agregando videos...")

            agregar_a_playlist_yt = youtube.playlistItems().insert(
                part='snippet',
                body={
                    "snippet": {
                        "playlistId": playlistId,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": videoId,
                        }
                    }
                }
            ).execute()

            videos.remove(videos[int(video_elegido) - 1])
            resp_1: str = input("\nSu video es una canción? (1 = Sí / ENTER = No)")

            if(resp_1 == '1'):
                resp_2:str = input("\nQuiere ver su letra? (1 = Sí / ENTER = No)")
                letra:str = mostrar_lyric(elegido[0: len(elegido) - 13])
                if(letra == ""):
                    print("\nNo fue posible encontrar la letra.")
                else:
                    print(letra)

            decision = input("\nDesea agregar otro video?: ")

def expotar_playlist_spotify(spotify: Spotify):
    '''pre:recibe la conexion con la api de spotify
       pos:exportar una playlist y sus canciones a
       un archivo csv
    '''
    playlists_elegida = listar_playlists(spotify, "si")

    playlist_nombre = playlists_elegida.name
    descripcion = [playlists_elegida.description]
    nombre_usuario = playlists_elegida.owner.display_name
    numero_canciones = playlists_elegida.tracks.total
    
    info = spotify.playlist(playlists_elegida.id)

    lista_canciones = []
   
    for cancion in info.tracks.items:
        
        nombre_cancion = cancion.track.name
        nombre_cancion = ['cancion : ',nombre_cancion]
        
        for artista in cancion.track.artists:
            artista = artista.name
        artista = ['artista : ',artista]
        cancion = [nombre_cancion,artista]
        lista_canciones.append(cancion)

    nombre_usuario = ['Nombre del usuario: ',nombre_usuario]
    playlist_nombre = ['Nombre de la playlist: ',playlist_nombre]
    numero_canciones = ['Numero de canciones : ',numero_canciones]
    descripcion = ['Descripcion : ',descripcion]

    try:
        with open('archivo_playlists.csv', 'w', newline='') as lista:
            datos = csv.writer(lista, delimiter=' ') 
            datos.writerow(nombre_usuario)
            datos.writerow(playlist_nombre)
            datos.writerow('Nombre de las canciones :')
        
            for canciones in lista_canciones:
                for cancion in canciones:
                    datos.writerow(cancion)
                
            datos.writerows(descripcion)
            datos.writerow(numero_canciones)
    except:
        print("Error con la apertura del archivo")

def obtener_id_playlist_creada(spotify: Spotify) -> str:
    """ PRE: recibe la conexion del tipo "Spotify" con la API
        POS: devuelve la id de la ultima playlist creada en spotify"""
    usuario = spotify.current_user() 
    playlists = spotify.playlists(usuario.id)
    playlistID = playlists.items[0].id
    return playlistID

def listar_playlists_spotify(spotify: Spotify) -> list:
    """ PRE: recibe la conexion del tipo "Spotify" con la API
        POS: retorna una lista de diccionarios con el id y el titulo de 
        todas las playlist en la cuenta de spotify"""
    lista_playlists_titulos: list = []
    dicc_aux: dict = dict()
    usuario = spotify.current_user() 
    playlists = spotify.playlists(usuario.id)
    for playlist_usuario in playlists.items:
        playlist_actual = spotify.playlist(playlist_usuario.id)
        dicc_aux = {
            "playlistId": playlist_usuario.id,
            "title": playlist_usuario.name
        }
        lista_playlists_titulos.append(dicc_aux)
    lista_playlists_titulos.append({"title":"Volver al menu"})
    i: int = 0
    print()
    print("Playlist:")
    for lista in lista_playlists_titulos:
        i+=1
        if i<len(lista_playlists_titulos):
            print(i,"- ***",lista["title"],"***")
        else:
            print(i,"-",lista["title"])

    return lista_playlists_titulos

def listar_canciones_spotify(
        spotify: Spotify, select_lista: int, lista_playlist: list) -> list:
    """ PRE: recibe la conexion del tipo "Spotify" con la API, un entero y 
        la lista extraida de la funcion anterior
        POS: retorna una lista con los titulos de las canciones en 
        la playlist elegida con el entero recibido"""
    print("Cargando canciones...")
    lista_canciones: list = list()
    usuario = spotify.current_user() #obtiene datos del usuario logueado
    playlists = spotify.playlists(usuario.id)
    for playlist_usuario in playlists.items:
        playlist_actual = spotify.playlist(playlist_usuario.id)
        if playlist_usuario.id == lista_playlist[select_lista-1]["playlistId"]:
            for cancion in playlist_actual.tracks.items:
                nombre_cancion = cancion.track.name
                lista_canciones.append(nombre_cancion)

    print()            
    if len(lista_canciones)==0:
        print("No hay canciones en esta lista")
    else:
        print("Playlist:",lista_playlist[select_lista-1]["title"])
        print("Canciones:")
        for cancion in lista_canciones:
                print('-', cancion)

        print()
    return lista_canciones

def buscador_spotify_para_sincronizar(
        spotify: Spotify, nombre_cancion, playlistID: str, 
        elementos_no_encontrados: list) -> list:
    """PRE: recibe la conexion del tipo "Spotify" con la API, el titulo de una cancion 
        y el id de la ultima playlist creada
        POS: devuelve una lista con los nombres de las canciones que no se encuentran en la plataforma"""
    mensaje = ("Buscando " + nombre_cancion + "... ")
    print(mensaje, end=" ")
    usuario_eleccion_elemento = "track"
    listado_elementos_encontrados: list = []  # lista de elementos encontrados
    for elementos in spotify.search(nombre_cancion, types=(usuario_eleccion_elemento,)):
        for usuario_eleccion_elemento in elementos.items:  # recorre cada elemento encontrado
            if len(listado_elementos_encontrados) < 1:
                listado_elementos_encontrados.append(usuario_eleccion_elemento)
    time.sleep(1) # si se hace todo de corrido, a veces da error de servidor, por eso se espera 1 segundo
    if len(listado_elementos_encontrados) > 0:
        spotify.playlist_add(playlistID, [listado_elementos_encontrados[0].uri])
        print("elemento agregado")  
    else:
        elementos_no_encontrados.append(nombre_cancion)
        print("no disponible en Spotify")

    return elementos_no_encontrados

def buscador_yotube_para_sincronizar(
        service_youtube, nombre_cancion: str, ultima_playlistId: str, 
        elementos_no_encontrados: list) ->list:
    """ PRE: recibe la conexion del tipo "Service_yotube" con la API, el titulo de una cancion 
        y el id de la ultima playlist creada
        POS: devuelve una lista con los nombres de las canciones que no se encuentran en la plataforma"""
    mensaje = ("Buscando " + nombre_cancion + "... ")
    print(mensaje, end=" ")
    search_in_youtube = service_youtube.search().list(q=nombre_cancion,part="id, snippet", maxResults=1).execute()
    time.sleep(1) # si se hace todo de corrido, a veces da error de servidor, por eso se espera 1 segundo
    if(search_in_youtube["items"] == []):
        elementos_no_encontrados.append(nombre_cancion)
        print("no disponible en youtube")

    else:
        videoId = search_in_youtube["items"][0]["id"]["videoId"]
        insertar_en_playlist_youtube(service_youtube, ultima_playlistId, videoId)
        print("elemento agregado")

    return elementos_no_encontrados

def selector(
        spotify, service_youtube, select_main: int, salida: str, select_lista: int, lista_playlist: list, 
        titulo: str, nombre_cancion: str, ultima_playlistId: str, elementos_no_encontrados: list):
    """Funciona como selector de funciones, redirige hacia una funcion en especifico segun sea necesario"""
    """ PRE: recibe todos los parametro necesarios para redirigir
        POS: en funcion del parametro salida y select_main, retorna lo necesario"""
    if select_main==1:
        if salida == "lista_playlist":
            lista_playlist = mostrar_playlist_youtube(service_youtube)
            return lista_playlist
        elif salida == "lista_canciones":
            lista_canciones = mostrar_canciones_playlist_youtube(service_youtube,select_lista,lista_playlist)
            return lista_canciones
        elif salida == "crear_lista":
            usuario_actual = spotify.current_user()
            spotify.playlist_create(usuario_actual.id, titulo)
            time.sleep(1) #darle tiempo al servidor para que al llamar nuevamente a las listas, incluya la ultima creada
            ultima_playlistId = obtener_id_playlist_creada(spotify)
            return ultima_playlistId 
        elif salida == "buscador":
            elementos_no_disponibles = buscador_spotify_para_sincronizar(
                spotify, nombre_cancion, ultima_playlistId, elementos_no_encontrados)
            titulo_archivo_cvs: str = "Elementos no encontrados en Spotify.csv"
            return elementos_no_encontrados, titulo_archivo_cvs

    else:
        if salida == "lista_playlist":
            lista_playlist = listar_playlists_spotify(spotify)
            return lista_playlist
        elif salida == "lista_canciones":
            lista_canciones = listar_canciones_spotify(spotify, select_lista, lista_playlist)
            return lista_canciones
        elif salida == "crear_lista":
            crear_playlist_youtube(service_youtube, titulo)
            time.sleep(1) #darle tiempo al servidor para que al llamar nuevamente a las listas, incluya la ultima creada
            lista_playlist = listar_playlists_youtube(service_youtube)
            ultima_playlistId = lista_playlist[0]["playlistId"]
            return ultima_playlistId
        elif salida == "buscador":
            elementos_no_disponibles = buscador_yotube_para_sincronizar(
                service_youtube, nombre_cancion, ultima_playlistId, elementos_no_encontrados)
            titulo_archivo_cvs: str = "Elementos no encontrados en Youtube.csv"
            return elementos_no_encontrados, titulo_archivo_cvs

def expotar_elementos_no_encontrados(
        titulo_archivo_csv: str, elemtos_no_encontrados: list) -> None:
    """Exporta un archivo csv con el titulo de los elementos que 
        no se encuentran en determinada plataforma"""
    """ PRE: recibe el nombre de la plataforma cuyo elemntos no se encuentran disponibles
        POS: no retona nada"""
    try:    
        with open(titulo_archivo_csv, "a", newline="") as archivo_csv:
            writer = csv.writer(archivo_csv, delimiter=",")
            for elemento in elemtos_no_encontrados:        
                writer.writerow([elemento])
        print("Elementos exportados en archivo csv")
    except:
        print("Ha ocurrido un error al escribir el archivo csv")

def sincronizar_playlist(service_youtube, spotify) -> None:
    """Procedimiento para sincronizar una playlist en ambas plataformas"""
    """ PRE: recibe ambas conexiones a las plataformas
        POS: no devuelve nada"""
    elementos_no_encontrados: list = list()
    i: int = 0
    texto_0: str = "Seleccione una opcion para sincronizar: "
    print("1 - Youtube a Spotify")
    print("2 - Spotify a Youtube")
    select_main = validar_ingreso_int(texto_0)
    while select_main not in [1,2]:
        print("Opcion invalida")
        select_main = validar_ingreso_int(texto_0)
    print()
    try:
        select_lista: int = int()
        lista_playlist: list = list()
        nombre_cancion: str = str()
        ultima_playlistId: str = str()
        titulo: str = str()
        print("Cargando listas...")
        lista_playlist = selector(
            spotify, service_youtube, select_main, "lista_playlist", 
            select_lista, lista_playlist, titulo, nombre_cancion, 
            ultima_playlistId, elementos_no_encontrados)
        texto_1: str = "Seleccione el nro de lista para ver las canciones en ella o vuelva al menu: "
        texto_2: str = "¿Desea exportar esta playlist?: "
        select_lista = validar_ingreso_int(texto_1)
        select: int = int()
        while select_lista != len(lista_playlist):
            if select_lista<1 or select_lista>len(lista_playlist):
                print("Opcion invalida")
                select_lista = validar_ingreso_int(texto_1)
            else:
                lista_canciones = selector(
                    spotify, service_youtube, select_main, "lista_canciones", 
                    select_lista, lista_playlist, titulo, nombre_cancion, 
                    ultima_playlistId, elementos_no_encontrados
                )
                if len(lista_canciones)==0:
                    select=2
                else:     
                    print()
                    print("1 - Si")
                    print("2 - No")
                    select = validar_ingreso_int(texto_2)
                while select not in [1,2]:
                    print("Opcion invalida")
                    select = validar_ingreso_int(texto_2)
                if select == 2:
                    print()
                    print("Playlist:")
                    i = 0
                    for lista in lista_playlist:
                        i+=1
                        if i<len(lista_playlist):
                            print(i,"- ***",lista["title"],"***")
                        else:
                            print(i,"-",lista["title"])
                    select_lista = validar_ingreso_int(texto_1)
                
                elif select == 1:
                    titulo = lista_playlist[select_lista-1]["title"]
                    print()
                    print("Sincronizando...")
                    try:
                        ultima_playlistId = selector(
                            spotify, service_youtube, select_main, "crear_lista", 
                            select_lista, lista_playlist, titulo, nombre_cancion, 
                            ultima_playlistId, elementos_no_encontrados
                        )
                        for nombre_cancion in lista_canciones:
                            elementos_no_disponibles=selector(
                                spotify, service_youtube, select_main, "buscador", 
                                select_lista, lista_playlist, titulo, nombre_cancion, 
                                ultima_playlistId, elementos_no_encontrados
                            )
                        print()
                        print("Playlist sincronizada")
                        if len(elementos_no_disponibles[0])>0:
                            print()
                            titulo_archivo_csv = elementos_no_disponibles[1]
                            print("Elementos no encontrados:")
                            for elemento in elementos_no_disponibles[0]:
                                print("-",elemento)
                            expotar_elementos_no_encontrados(
                                titulo_archivo_csv, elementos_no_disponibles[0])
                            elementos_no_encontrados = []
                        print()
                    except:
                        print("Ha ocurrido un error durante la sincronizacion, por favor intentelo de nuevo")
                    print("Playlist:")
                    i = 0
                    for lista in lista_playlist:
                        i+=1
                        if i<len(lista_playlist):
                            print(i,"- ***",lista["title"],"***")
                        else:
                            print(i,"-",lista["title"])
                    select_lista = validar_ingreso_int(texto_1)
    except:
        print("Ha ocurrido un error, por favor intentelo de nuevo")       


def nube_de_palabras(letras_playlist : list):
    '''pre: recibe las letras de canciones de determinada playlist
       pos: muesta una imagen de nube de plabras con las 
       palabras mas usadas
    '''
    try:
        #El contenido: 
        stopwords = set(STOPWORDS)
        letras = " ".join(letras_playlist)
        #La apariencia:
        imagen = np.array(Image.open('nube.png'))
        wc = WordCloud(background_color = 'white',
            max_words = 10,
            max_font_size = 80,
            stopwords = stopwords,
            mask = imagen
        )
        wc.generate(letras)

        #Graficado
        plt.imshow(wc, interpolation = 'bilinear')
        plt.axis('off')
        plt.show()
    except ValueError:
        print('Error, no se hallaron canciones en la playlist')


def ranking_palabras_YT(youtube) -> None:
    i = 0
    print('\nPara cual playlist de YT va a querer su ranking?')
    todas_las_playlist = listar_playlists_youtube(youtube)

    for playlist in todas_las_playlist:
        i += 1
        print(f"{i} - {playlist['title']}")

    respuesta = int(input("\nDe cuál playlist querrá el ranking?"))
    respuesta = respuesta - 1 # La respuesta le resto uno para que coincida con la posicion real de la playlist.
                              # Ya que en los diccionarios se empieza a contar desde el 0 (cero).
    playlist_elegida = todas_las_playlist[respuesta]
    lista_letras: list = []

    elementos_de_playlist = youtube.playlistItems().list(
        playlistId = playlist_elegida['playlistId'],
        part = "snippet",
        maxResults = 50
    ).execute()

    for video in elementos_de_playlist["items"]:
        titulo_video = video["snippet"]["title"]
        letra: str = mostrar_lyric(titulo_video)
        if(letra != ""):
            lista_letras.append(letra)

    nube_de_palabras(lista_letras)

def ranking_palabras_Spotify(spotify: Spotify) -> None:
    l_playlist: list = []
    lista_letras: list = []
    y: int = 0
    p: int = 0
    usuario = spotify.current_user() 
    playlists = spotify.playlists(usuario.id)

    for playlist_usuario in playlists.items:
        y += 1
        nombre_playlist = playlist_usuario.name
        print(f'\n{y} --> {nombre_playlist}. ')
    escoger_playlist: int = int(input("Cual playlist elegís: "))

    while(escoger_playlist > y):
        escoger_playlist: int = int(input("Cual playlist elegís: "))

    for playlist_usuario in playlists.items:
        p += 1
        if(p == escoger_playlist):
            playlist_elegida = spotify.playlist(playlist_usuario.id)
            for cancion in playlist_elegida.tracks.items:
                nombre_cancion = cancion.track.name
                letra = mostrar_lyric(nombre_cancion)
                if(letra != ""):
                    lista_letras.append(letra)
    nube_de_palabras(lista_letras)
	
	
def menu() -> int:
    """Menu"""
    """ PRE: no recibe nada
        POS: retorna la seleccion del menu"""
    i: int = 0
    print()
    lista_menu: list = [
        "Autenticarse, ver usuario actual o cambiar usuario en Youtube",
        "Autenticarse en Spotify",
        "Listar Playlists actuales para Youtube",
        "Listar Playlists actuales para Spotify",
        "Exportar una playlist de Youtube",
        "Exportar una playlist de Spotify",
        "Crear una nueva playlist en Youtube",
        "Crear una nueva playlist en Spotify",
        "Buscar canciones/videos en YouTube y agregarlos a una playlist",
        "Buscar elementos en Spotify (Agregarlos a playlists o ver letras de canciones)",
        "Sincronizar una playlist en ambas plataformas",
        "Nube de palabras de una playlist",
        "Salir"
    ]
    print("***MENU***")
    for opcion in lista_menu:
        i += 1
        print(i,"-",opcion)
    texto: str = "Ingrese una opcion: "
    select = validar_ingreso_int(texto)
    while select<1 or select>len(lista_menu):
        print("Opcion invalida")
        select = validar_ingreso_int(texto)
    return select

def main():
    select_menu = menu()
    sesion_youtube: bool = False
    sesion_spotify: bool = False
    while select_menu != 13:
        if select_menu == 1:
            service_youtube = sub_menu_acceso_youtube()
            sesion_youtube = service_youtube[1]
        elif select_menu == 2:
            spotify = acceso_spotify()
            if spotify != None:
                print(' --- LOGUEO EXITOSO ---')
                sesion_spotify = True
            else:
                print('Fallo conexion con Spotify, vuelva a intertarlo ')
        elif select_menu == 3 and sesion_youtube ==True:
            listar_playlist_y_temas_youtube(service_youtube[0])
        elif select_menu == 4 and sesion_spotify == True:
            listar_playlists(spotify, 'no')
        elif select_menu == 5 and sesion_youtube == True:
            expotar_playlist_youtube(service_youtube[0])
        elif select_menu == 6 and sesion_spotify == True:
                expotar_playlist_spotify(spotify)
        elif select_menu == 7 and sesion_youtube == True:
            crear_lista_de_reproduccion_youtube(service_youtube[0])
        elif select_menu == 8 and sesion_spotify == True:
            crear_playlist_spotify(spotify)
        elif select_menu == 9 and sesion_youtube == True:
            buscador_youtube(service_youtube[0])
        elif select_menu == 10 and sesion_spotify == True:
            buscador_spotify(spotify)
        elif select_menu == 11 and sesion_youtube == True and sesion_spotify == True:
                sincronizar_playlist(service_youtube[0], spotify)
        elif select_menu == 12 :
            print('Desea realizarlo a travez de spotify o Youtube?')
            opcion = input('Ingrese opcion s/y: ')
            if opcion == 'y' and sesion_youtube == True:
                ranking_palabras_YT(service_youtube[0])
            elif opcion == 's' and sesion_spotify == True:
                ranking_palabras_Spotify(spotify)
            elif opcion != 's' and opcion != 'y':
                print('Caracter ingresado incorecto')
            else:
                print('Debe iniciar sesion primero')
        elif select_menu in [3,5,7,9,11,12] and sesion_youtube == False:
            print("Antes debe iniciar sesion en youtube")
        elif select_menu in [4,6,8,10,11,12] and sesion_spotify == False:
            print("Antes debe iniciar sesion en spotify")  

        select_menu = menu()                
main()
