import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def acceso_youtube():
    credentials = None
    #ver que las credenciales sigan siendo validas o crearlas
    if os.path.exists("token.pickle"):
        print("Ingreso a youtube exitoso")
        with open("token.pickle","rb") as token:                #"rb" read binary
            credentials = pickle.load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print("Ingreso a youtube exitoso")
            credentials.refresh(Request())

        else:
            print("Ingreso a youtube exitoso")
            flow = InstalledAppFlow.from_client_secrets_file("clave.json",
                scopes=["https://www.googleapis.com/auth/youtube.readonly"])

            flow.run_local_server(port=8080, prompt="consent", authorization_prompt_message="")#prompt es para recibir el token de actualizacion
            credentials = flow.credentials

            #Guardar las credenciales en un archivo pickle
            with open("token.pickle", "wb") as f:
                pickle.dump(credentials, f)

    return credentials  




def opcion_1():
    pass

def opcion_2():
    pass

def opcion_3():
    pass

def opcion_4():
    pass
def opcion_5():
    pass
def opcion_6():
    pass
def opcion_7():
    pass
def main():
    menu: int = 1
    while menu == 1:
        print('MENU')
        print('1- ')
        print('2- ')
        print('3- ')
        print('4- ')
        print('5- ')
        print('6- ')
        print('7- ')
        print('8- SALIR')
        opcion: str = input('Elija opcion (1,2,3,4,5,6,7,8): ')
        while opcion not in ('1', '2', '3', '4', '5', '6', '7', '8'):
            opcion = input('Incorrecto, elija una opcion valida: ')

        if opcion == '1':
            credentials = acceso_youtube()
        elif opcion == '2':
            opcion_2()
        elif opcion == '3':
            opcion_3()
        elif opcion == '4':
            opcion_4()
        elif opcion == '5':
            opcion_4()
        elif opcion == '6':
            opcion_4()
        elif opcion == '7':
            opcion_4()
        elif opcion == '8':
            exit()

        volver_menu = input('\nPresione ENTER para volver al menu')


main()
