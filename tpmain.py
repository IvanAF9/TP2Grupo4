import tekore as tk
from tekore import RefreshingToken, Spotify
import os
import pickle
import csv
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


def acceso_youtube():
    credentials = None
    # ver que las credenciales sigan siendo validas o crearlas
    if os.path.exists("token.pickle"):
        print("Ingreso a youtube exitoso")
        with open("token.pickle", "rb") as token:  # "rb" read binary
            credentials = pickle.load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print("Ingreso a youtube exitoso")
            credentials.refresh(Request())

        else:
            print("Ingreso a youtube exitoso")
            flow = InstalledAppFlow.from_client_secrets_file("clave.json",
                                                             scopes=["https://www.googleapis.com/auth/youtube"])

            flow.run_local_server(port=8080, prompt="consent",
                                  authorization_prompt_message="")  # prompt es para recibir el token de actualizacion
            credentials = flow.credentials

            # Guardar las credenciales en un archivo pickle
            with open("token.pickle", "wb") as f:
                pickle.dump(credentials, f)

    return credentials


def acceso_spotify() -> Spotify:
    '''Genera conexion con spotify a traves del id_cliente y cliente_secreto
    	PRE: No recibe nada
    	POS: Devuelve la conexion del tipo "Spotify" con la API'''

    print('\nEstá a punto de ser enviado a Spotify para pedir autorización a su cuenta.')
    print(f'Luego de eso será redireccionado a otra pagina y el programa le pedirá que copie el link al que fue redireccionado.')
    input_usuario = input('Presione ENTER para continuar: \n')
    id_cliente = '4e1bc2b1c16e4005b0b53b549ee818d4'
    cliente_secreto = '27e3e8415ef44fe997e731d830ec5541'
    redireccion_uri = 'https://github.com/IvanAF9/TP2Grupo4'
    conf = (id_cliente, cliente_secreto, redireccion_uri)

    token_usuario = tk.prompt_for_user_token(*conf, scope=tk.scope.every) #pide permisos al usuario y redirecciona, devuelve token
    return tk.Spotify(token_usuario) #Inicia la conexion a la API Spotify

def listar_playlists(spotify: Spotify, solo_mostrar_titulo_playlist: str):
    '''Hace un print de las playlists del usuario actual por cancion y artista
	PRE: Recibe la conexion del tipo "Spotify" con la API
	POS: Devuelve playlist elegida por usuario solamente si solo_mostrar_titulo_playlist es igual a "si" '''
    lista_playlists_titulos: list = []
    usuario = spotify.current_user() #obtiene datos del usuario logueado
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
                if hasattr(cancion.track, 'artists'): #comprueba si el objecto cancion.track contiene el atributo artists, ya que si no devuelve error
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

    '''Comentarios para el equipo:
    Los objectos que devuelven las funciones de tekore tienen atributos.
    Estos objetos se ven de la siguiente manera:
    Objecto: Playlist
    Atributos: id: 4564512531
               nombre: nombre de la playlist
               foto de la playlist: 48451515
               etc.
    Para invocar estos atributos simplemente se pone nombre_del_objeto.atributo
    A su vez un atributo dentro de un objeto, puede ser tambien un objeto con sub atributos, y de esa manera es guardada la información de canciones
    dentro de una playlist, con sub-objetos.
    Por ejemplo playlist_actual.tracks.items es un objeto que contiene atributos de las canciones de la playlist
    En la documentación de tekore figuran los objetos y sus atributos que devuelven las funciones, esto esta en:
    https://tekore.readthedocs.io/en/stable/reference/client.html
    '''


def mostrar_letra_cancion(spotify: Spotify):
    pass
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
                mostrar_letra_cancion(spotify)
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
                print(f'{i + 1}: {listado_elementos_encontrados[i].name}')
        else:
            for i in range(len(listado_elementos_encontrados)):
                print(f'{i + 1}: {listado_elementos_encontrados[i].name}')

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
            pass
    else:
        print('\nNo se ha encontrado resultados para su busqueda')

        

def listar_playlists_youtube(credentials):
    youtube = build("youtube", "v3", credentials=credentials)

    requests = youtube.playlists().list(part="contentDetails, snippet", mine=True, maxResults=50)

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


def crear_lista_de_reproduccion_youtube(credentials):
    youtube = build("youtube", "v3", credentials=credentials)
    nueva_lista: str = input("Ingrese el nombre de la lista a crear: ")

    # crear la playlist

    playlists_insert_response = youtube.playlists().insert(
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
    print("Lista creada")

    """Comentario, el codigo que sigue es para dar la opcion de ingresar las canciones que tiene el canal propio,
    la duda es si las canciones estan en el canal o no
    #se debe esperar un segundo antes de solicitar una nueva respuesta del servidor
    input("espera")

    lista_aux = ver_listas_de_reproduccion_youtube(youtube)



    for elemento in lista_aux:
        if nueva_lista==elemento["title"]:
            playlist_Id=elemento["playlistId"]

    #busca todos los videos
    channels_response = youtube.channels().list(
      mine=True,
      part="contentDetails"
    ).execute()

    for channel in channels_response["items"]:
        uploads_list_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]

    playlistitems_list_request = youtube.playlistItems().list(

      part="snippet",
      playlistId=uploads_list_id
    ).execute()

    #crear una lista de diccionarios con el titulo del video y su id
    for playlist_item in playlistitems_list_request["items"]:
        title = playlist_item["snippet"]["title"]
        video_id = playlist_item["snippet"]["resourceId"]["videoId"]

    print("1 - ",title)
    seleccion = input("Selecciones el video a agregar a la lista: ")

    if seleccion=="1":
        video=video_id

    youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId":playlist_Id,
                "resourceId":{
                    "kind": "youtube#video",
                    "videoId": video
                }
            }
        }).execute()"""


def expotar_playlist_youtube(credentials):
    '''pre:recibe las credenciales
       pos:exportar una playlist y sus videos a
       un archivo csv
    '''
    youtube = build('youtube', 'v3', credentials=credentials)
    lista_playlist = listar_playlists_youtube(credentials)
    contador = 0

    for lista in lista_playlist:
        contador = + 1
        print(contador, lista["title"])

    numero_playlist = input('Ingrese el numero de la playlist que desea exportar: ')
    id = lista_playlist[numero_playlist - 1]["playlistId"]
    nombre_playlist = lista_playlist[numero_playlist - 1]["title"]

    playlist = youtube.playlistItems().list(
        part='snippet',
        playlistId=id,
        maxResults=50
    )
    playlist = playlist.execute()
    nombre_videos = []
    print('videos:')
    for item in playlist['items']:
        print('_ ', item['snippet']['title'])
        nombres = item['snippet']['title']
        nombre_videos.append(nombres)

    with open('archivo_playlists.csv', 'w', newline='') as lista:
        datos = csv.writer(lista, delimiter=' ')
        datos.writerow('Playlist:')
        datos.writerow(nombre_playlist)
        datos.writerows(nombre_videos)


def main():
    logueo_spotify = 0
    logueo_youtube = 0
    menu: int = 1
    while menu == 1:
        print('MENU')
        print('1- Autenticarse en Youtube')
        print('2- Autenticarse en Spotify')
        print('3- Listar Playlists actuales para Youtube')
        print('4- Listar Playlists actuales para Spotify')
        print('5- Exportar una playlist de youtube')
        print('6- Crear una nueva playlist en Youtube')
        print('7- Buscar elementos en Spotify y agregarlos a una playlist')
        print('8- SALIR')
        opcion: str = input('Elija opcion (1,2,3,4,5,6,7,8): ')
        while opcion not in ('1', '2', '3', '4', '5', '6', '7', '8'):
            opcion = input('Incorrecto, elija una opcion valida: ')

        if opcion == '1':
            credentials = acceso_youtube()
            logueo_youtube = 1
        elif opcion == '2':
            spotify = acceso_spotify()
            print(' --- LOGUEO EXITOSO ---')
            logueo_spotify = 1
        elif opcion == '3':
            if logueo_youtube == 0:
                print('Antes de buscar información en Youtube, deberá loguearse en el MENU')
            else:
                lista_playlist = listar_playlists_youtube(credentials)
                for lista in lista_playlist:
                    print(lista["title"])
        elif opcion == '4':
            if logueo_spotify == 0:
                print('Antes de buscar información en Spotify, deberá loguearse en el MENU')
            else:
                listar_playlists(spotify, 'no')
        elif opcion == '5':
            if logueo_youtube == 0:
                print('Antes de buscar información en Youtube, deberá loguearse en el MENU')
            else:
                expotar_playlist_youtube(credentials)
        elif opcion == '6':
            if logueo_youtube == 0:
                print('Antes de buscar información en Youtube, deberá loguearse en el MENU')
            else:
                crear_lista_de_reproduccion_youtube(credentials)
        elif opcion == '7':
            if logueo_spotify == 0:
                print('Antes de buscar información en Spotify, deberá loguearse en el MENU')
            else:
                buscador_spotify(spotify)
        elif opcion == '8':
            menu = 2

        if menu == 1:
            volver_menu = input('\nPresione ENTER para volver al menu')


main()
