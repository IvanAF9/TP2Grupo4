import tekore as tk
from tekore import RefreshingToken, Spotify
import os
import pickle
import csv
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build



def acceso_youtube():
    credentials = None
    # ver que las credenciales sigan siendo validas o crearlas
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:  # "rb" read binary
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

                flow.run_local_server(port=8080, prompt="consent", authorization_prompt_message="")#prompt es para recibir el token de actualizacion
                credentials = flow.credentials

                #Guardar las credenciales en un archivo pickle
                with open("token.pickle", "wb") as f:
                    print("Inicio de sesion exitoso")
                    pickle.dump(credentials, f)

        service_youtube= build("youtube", "v3", credentials=credentials)         
        return service_youtube

    except:
        print("No hay conexion a internet")
                
        return None


def channel_request(service_youtube) -> str:
    canal = service_youtube.channels().list(part="statistics", mine=True).execute()
    id_canal = canal["items"][0]["id"]
    return id_canal
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

        

def listar_playlists_youtube(service_youtube) -> list:
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
    select = input(texto)
    es_numerico = select.isnumeric()

    while es_numerico!=True:
        print("Opcion invalida")
        select = input(texto)
        es_numerico = select.isnumeric()

    select = int(select)

    return select


def sub_menu_acceso_youtube():
    sesion_iniciada = False
    lista_usuarios: list = {
            "UC_AWnHXFjISHh3Kn9CFWc6A":"ellocomauro376@gmail.com",
            "channelId":"id de otro canal",
    }
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
    while select!=4:
        while select>4:
            print("Opcion invalida")
            select = validar_ingreso_int(texto)
        if select==1:
            print()
            service_youtube = acceso_youtube()
            print("Sesion iniciada")
            sesion_iniciada = True

        elif select ==2:
            print()
            if os.path.exists("token.pickle"):
                service_youtube = acceso_youtube()
                id_canal = channel_request(service_youtube)
                print("Usuario actual:",lista_usuarios[id_canal])
                sesion_iniciada = True
                #hacer request para obtener el id del canal y asociarlo a la lista_usuario
                #imprimir el nombre
            else:
                print("No existe usuario actual")
        elif select==3:
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

def listar_playlist_y_temas_youtube(service_youtube):
    print("Cargardo listas...")
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
    texto: str = "Seleccione el nro de lista para ver las canciones en ella o vuelva al menu: "
    select = validar_ingreso_int(texto)
    while select != len(lista_playlist):
        if select>len(lista_playlist):
            print("Opcion invalida")
            select = validar_ingreso_int(texto)
        else:
            print("Cargando canciones...")
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

            print()
            i = 0
            print("Playlist:")
            for lista in lista_playlist:
                i+=1
                if i<len(lista_playlist):
                    print(i,"- ***",lista["title"],"***")
                else:
                    print(i,"-",lista["title"])
            select = validar_ingreso_int(texto)
    
def ver_todos_los_temas_youtube(service_youtube) -> list:
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
                "title":item['snippet']['title'],
                "videoid":item["snippet"]["resourceId"]["videoId"]
            }
            lista_aux.append(dicc_aux)

        for i in range(len(lista_aux)):
            for j in range(len(lista_aux)):
                if i!=j and i<len(lista_aux) and j<len(lista_aux):
                    if lista_aux[i]["videoid"]==lista_aux[j]["videoid"]:
                        lista_aux.remove(lista_aux[j])

    return lista_aux 

def crear_lista_de_reproduccion_youtube(service_youtube):
    nueva_lista: str = input("Ingrese el nombre de la lista a crear: ")
    print("Creando lista de reproduccion...")
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
    print("Lista creada")
    print("Cargando canciones...")
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
    lista_playlist = listar_playlists_youtube(service_youtube)
    for title in lista_playlist:
        if title["title"]==nueva_lista:
            playlistId=title["playlistId"]
            break
    select = validar_ingreso_int(texto)
    while select != len(lista_temas):
        if select>len(lista_temas):
            print("Opcion invalida")
        else:
            print("Listando cancion...")
            insertar_tema = service_youtube.playlistItems().insert(
                part='snippet',
                body={
                    "snippet":{
                        "playlistId":playlistId,
                        "resourceId":{
                            "kind":"youtube#video",
                            "videoId":lista_temas[select-1]["videoid"]
                        }
                    }

                }
            ).execute()
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
    print("videos:")
    for item in playlist['items']:
        print('_ ', item['snippet']['title'])
        nombres = item['snippet']['title']
        nombre_videos.append(nombres)
        descripcion = item['snippet']['description']
        titulo = item['snippet']['title']
        channel_id = item['snippet']['channelId']
        time = item['snippet']['publishedAt']

    nombre_playlist = ('-Playlist: ',titulo)
    atributos = ('-Titulo de la playlist: ', titulo, '-Id del canal: ', channel_id, '-Tiempo de subida: ', time)
    descripcion_general = ('-Descripcion general: ', descripcion)

    with open('archivo_playlists.csv', 'w', newline='') as lista:
        datos = csv.writer(lista, delimiter=' ')
        datos.writerow(nombre_playlist)
        datos.writerows(nombre_videos)
        datos.writerow(atributos)
        try:
            datos.writerow(descripcion_general)
        except UnicodeEncodeError:
            print('Hubo un error con la descipcion, por un caracter no aceptado')

	
def buscador_youtube(youtube):

    print("Buscador de YouTube. Que desea ver?")
    print("\nEscriba lo que quiera buscar (nombre de video, nombre de canal, cantante, etc)")
    
    busqueda: str = input("-- ")

    y: int = -1

    search_in_youtube = youtube.search().list(

        order = "viewCount",
        part = f"{busqueda}, snippet",
        maxResults = 3

    ).execute()

    videos: list = []
    
    print("\nLos videos que se encontraron son (según reproducciones): ")

    for resultado in search_in_youtube.get("items", []):

        y += 1

        if search_in_youtube[busqueda]["kind"] == "youtube#video":

            videos.append("%s (%s)" % (resultado["snippet"]["title"],
                                 resultado["id"]["videoId"]))

        print(f"\n1- {videos[y]}")	
	


def main():
    logueo_spotify = 0
    logueo_youtube = 0
    menu: int = 1
    while menu == 1:
        print('MENU')
        print('1- Autenticarse, ver usuario actual o cambiar usuario en Youtube')
        print('2- Autenticarse en Spotify')
        print('3- Listar Playlists actuales para Youtube')
        print('4- Listar Playlists actuales para Spotify')
        print('5- Exportar una playlist de youtube')
        print('6- Crear una nueva playlist en Youtube')
        print('7- Buscar elementos en Spotify y agregarlos a una playlist')
        print('8- Buscar canciones/videos en YouTube.')
        print('9- SALIR')
        opcion: str = input('Elija opcion (1,2,3,4,5,6,7,8,9): ')
        while opcion not in ('1', '2', '3', '4', '5', '6', '7', '8', '9'):
            opcion = input('Incorrecto, elija una opcion valida: ')
	
        if opcion == '1':
            service_youtube = sub_menu_acceso_youtube()
            if service_youtube[1]==True:
                logueo_youtube = 1
        elif opcion == '2':
            spotify = acceso_spotify()
            print(' --- LOGUEO EXITOSO ---')
            logueo_spotify = 1
        elif opcion == '3':
            if logueo_youtube==0:
                print('Antes de buscar información en Youtube, deberá loguearse en el MENU')
            else:
                listar_playlist_y_temas_youtube(service_youtube[0])
        elif opcion == '4':
            if logueo_spotify == 0:
                print('Antes de buscar información en Spotify, deberá loguearse en el MENU')
            else:
                listar_playlists(spotify, 'no')
        elif opcion == '5':
            if logueo_youtube == 0:
                print('Antes de buscar información en Youtube, deberá loguearse en el MENU')
            else:
                expotar_playlist_youtube(service_youtube[0])
        elif opcion == '6':
            if logueo_youtube == 0:
                print('Antes de buscar información en Youtube, deberá loguearse en el MENU')
            else:
                crear_lista_de_reproduccion_youtube(service_youtube[0])
        elif opcion == '7':
            if logueo_spotify == 0:
                print('Antes de buscar información en Spotify, deberá loguearse en el MENU')
            else:
                buscador_spotify(spotify)
        elif opcion == '8':
            if logueo_youtube == 0:
                print('Antes de buscar información en Youtube, deberá loguearse en el MENU')
            else:
                buscador_youtube(service_youtube[0])

        elif opcion == '9':
            menu = 2

        if menu == 1:
            volver_menu = input('\nPresione ENTER para volver al menu')


main()
