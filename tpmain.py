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
            opcion_1()
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