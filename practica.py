import pycreate2
from math import pi, sin, cos, atan2, sqrt
import time

if __name__ == "__main__":
    # Crea un Bot (Create2)
    port = 'COM3'
    baud = {
        'default': 115200,
        'alt': 19200  
    }
    
    bot = pycreate2.Create2(port=port, baud=baud['default'])
    
    bot.start()
    bot.full()

Rx2=72 # mm
nCe=508.8
D_ENTRERUEDAS = 235 # mm
FACTOR_CONVERSION = Rx2*pi/nCe
VELOCIDAD_MOTORES = 150
VALORMAX_ENCODER = 65535 


#Funcion verificarSalto:
# Toma valores anterior y actual de un encoder y segun velocidad y giro,
#  devuelvo el salto de 65535 a 0 o viceversa si corresponde, sino 0.
def verificarSalto(valEncoderActual, valEncoderAnterior, saltoAnterior):
    
    if saltoAnterior != 0: #Si ha ocurrido un salto, lo devuelvo para que no existan problemas.
        return saltoAnterior
    if (valEncoderActual - valEncoderAnterior) > 60000: #60000 cuentas "de mas" en encoder, en diferencia entre lectura actual y anterior
        #Retorno -65535 ya que el salto fue desde la lectura anterior,
        #  ha sumado aprox. 60000, es decir pasa de 0 a 65535 en un momento dado entre dos lecturas
        return -65535 
    elif (valEncoderAnterior - valEncoderActual) > 60000: #60000 cuentas pero en sentido contrario, entonces retorno 65535
        return 65535
    else:
        return 0
#####

#Funcion actuar: 
# Toma: -valor deseado (en mm o en radianes segun que actuacion quiero realizar), 
#       -velocidad para indicar hacia donde avanzar: Retroceder/Avanzar o Giro derecha/izquierda dependiendo de giro 
#       -giro, que es =1 si el movimiento es un giro.
# Devuelve sRecorrido (delta_s) y titaRecorrido (delta_tita)
def actuar(valor, velocidad, giro=0):

    #Tomo valores iniciales de encoders
    sensores = bot.get_sensors()
    sEncoderIzq_Inicial = sensores.encoder_counts_left  * FACTOR_CONVERSION 
    sEncoderDer_Inicial = sensores.encoder_counts_right * FACTOR_CONVERSION
    #Inicializo las variables para calcular salto:
    encoderDerAnterior = sensores.encoder_counts_right
    encoderIzqAnterior = sensores.encoder_counts_left
    #Calculo s_inicial y tita_inicial
    s_Inicial = (sEncoderDer_Inicial + sEncoderIzq_Inicial) / 2
    tita_Inicial = (sEncoderDer_Inicial - sEncoderIzq_Inicial) / D_ENTRERUEDAS #En radianes!


    time.sleep(0.5)
    if giro: #Si giro hacia la derecha, la velocidad sera dada positivo, sino negativa, generando el giro deseado
        bot.drive_direct(velocidad, -velocidad) #gira hacia derecha si velocidad<0, sino hacia izquierda
    else:
        bot.drive_direct(velocidad, velocidad)

    valor_actual = 0 #Inicializo la distancia recorrida/angulo recorrido en 0
    vueltaEncoderIzq = vueltaEncoderDer = 0 #variable que guarda salto si es necesario

    while(valor_actual < valor): 
        time.sleep(0.001)
        sensores = bot.get_sensors()

        #Nota: Si el encoder salta de 65535 a 0 o viceversa, el movimiento se corrompe, por ende se usan
        # las variables vueltaEncoderXxx para que el salto no se cuente al realizar calculos.
        vueltaEncoderIzq = verificarSalto(sensores.encoder_counts_left, encoderIzqAnterior, vueltaEncoderIzq)
        vueltaEncoderDer = verificarSalto(sensores.encoder_counts_right, encoderDerAnterior, vueltaEncoderDer)

        sEncoderIzq = (sensores.encoder_counts_left + vueltaEncoderIzq) * FACTOR_CONVERSION 
        sEncoderDer = (sensores.encoder_counts_right + vueltaEncoderDer) * FACTOR_CONVERSION 
        
        if velocidad < 0: #Segun si retrocedo o avanzo, mido la distancia recorrida hacia delante o hacia atras
            sRecorrido = s_Inicial - ( (sEncoderIzq + sEncoderDer) / 2 )
            titaRecorrido = tita_Inicial - ( (sEncoderDer - sEncoderIzq) / D_ENTRERUEDAS )  
        else: 
            sRecorrido = ( (sEncoderIzq + sEncoderDer) / 2 ) - s_Inicial
            titaRecorrido = ( (sEncoderDer - sEncoderIzq) / D_ENTRERUEDAS ) - tita_Inicial 
              
        if giro:
            valor_actual = titaRecorrido
        else:
            valor_actual = sRecorrido

        encoderDerAnterior = sensores.encoder_counts_right
        encoderIzqAnterior = sensores.encoder_counts_left
        
        
    bot.drive_stop()
    #Dado a como se calcularon los valores, al retroceder o girar antihoriamente, 
    # debo invertir los valores para corresponderse a la realidad:
    if velocidad<0: 
        sRecorrido = -sRecorrido
        titaRecorrido = -titaRecorrido
    
    return sRecorrido, titaRecorrido
#####

#Funcion Desplazarse: Avanza/Retrocede segun "retrocedo" y el "valor" deseado. 
# Devuelve delta_s y delta_tita para calcular odometria
def desplazarse(valor,retrocedo=0): 
    velocidad = VELOCIDAD_MOTORES
    valor = int(valor) # Si no es entero, no puede convertir y se genera excepcion

    if(valor > 1000 or valor < 1): # Condicion para que no exceda valores incorrectos
        raise Exception("Ingresar valores entre 1 y 1000 mm")
    
    if retrocedo:
        velocidad = -VELOCIDAD_MOTORES #Si es para retroceder, cambio sentido de movimiento en motores.

    delta_s, delta_tita = actuar(valor, velocidad)
    
    return delta_s, delta_tita
#####

#Funcion Girar: Gira en sentido horario ("haciaDerecha"=1) / antihorario ("haciaDerecha"=0 es decir "hacia izquierda") el "valor" en grados dado. 
# Devuelve delta_s y delta_tita para calcular odometria
def girar(valor, haciaDerecha=0): 
    velocidad = VELOCIDAD_MOTORES
    valor = int(valor) # Si no es entero, no puede convertir y se genera excepcion

    if(valor > 1000 or valor < 1): # Condicion para que no exceda valores incorrectos
        raise Exception("Ingresar valores entre 1 y 1000 grados")
    
    if haciaDerecha:
        velocidad = -VELOCIDAD_MOTORES #Si es para girar en sentido horario, cambio sentido de movimiento en motores.
    
    #Debo convertir los grados deseados a radianes ya que es lo que se utiliza en la funcion actuar
    valor_rad = valor * pi / 180
    delta_s, delta_tita = actuar(valor_rad, velocidad, giro=1)
    
    return delta_s, delta_tita
#####

### Tarea autonoma: ir a coordenadas (x,y)
def ir_coordenadas(x_deseado, y_deseado):

    global x, y, tita
    delta_y = int(y_deseado)-y
    delta_x = int(x_deseado)-x

    tita_necesario = atan2(delta_y,delta_x)*180/pi #tita necesario que girar debido a delta_x y delta_y
    desp_necesario = int(sqrt( delta_x**2 + delta_y**2 ))
    #print("tita,desp necesarios:",tita_necesario,desp_necesario)
    #print("tita actual:", tita*180/pi)

    #Calculo tita de giro total: resto los titas y le sumo 180 para trasladar a valores no muy grandes
    # Utilizo modulo una vez traladado el angulo a valores normales, aplico modulo [0°,360°] y resto 180 para que el giro sea entre [-180°,180°]
    tita_giroTotal = int( (tita_necesario - tita*180/pi + 180) % 360 ) - 180  
    #Giro antihorario ("haciaDerecha"=0) u horario ("haciaDerecha"=1) segun el valor del angulo:
    if tita_giroTotal < 0:
        s_giro, tita_giro = girar(abs(tita_giroTotal), haciaDerecha=1)
    elif tita_giroTotal > 0:
        s_giro, tita_giro = girar(tita_giroTotal, haciaDerecha=0)
    cargar_odometria(s_giro,tita_giro,"Mov.coord - giro")

    #print("S_giro:",s_giro, ", tita_giro:",tita_giro)
    #Me muevo el desplazamiento necesario
    s_desp, tita_desp = desplazarse(desp_necesario)
    cargar_odometria(s_desp, tita_desp,"Mov.coord - desplazamiento") 

    print("Se ha llegado al destino: (", x, y, ")\n")
#####

### Tarea autonoma: moverse por un cuadrado segun el 'tamano' deseado
def moverse_cuadrado(tamano):
    s, tita = desplazarse(tamano)
    cargar_odometria(s, tita,"Cuadrado - desplazamiento")
    for i in range(3): 
        s, tita = girar(90)
        cargar_odometria(s, tita,"Cuadrado - giro") 
        s, tita = desplazarse(tamano)
        cargar_odometria(s, tita,"Cuadrado - desplazamiento")    
    print("Cuadrado realizado.")
#####

### ODOMETRIA:

#Funcion para mostrar la odometria: historico de posiciones y posicion actual
def mostrar_odometria():
    global historico, x, y, tita
    print("\nHistorico:")
    i = 0
    for posicion in historico:
        print("[ pos.",i,"-",posicion["tipo"],"]: x:",round(posicion["x"],2)," mm, y:",round(posicion["y"],2),"mm, tita:",round(posicion["tita"]*180/pi,1),"°")
        i+=1
    #Muestro posicion actual
    print("Posicion actual","x:",round(x,3),"mm, y:",round(y,3),"mm, tita:",round(tita*180/pi,1),"°")
#####

# Calculo la odometria y la cargo en las variables globales de historico y posicion actual
def cargar_odometria(delta_s, delta_tita, tipo):
    global historico, x, y, tita
    print("\nCalculando odometria y cargando valores")
    print("Posicion anterior (x, y, tita):",round(x,2), round(y,2), round(tita*180/pi,1))
    print("Deltas de movimiento (delta_s, delta_tita):", delta_s, delta_tita)
    print("Tipo de movimiento: ", tipo)
    #calculo delta_x y delta_y segun trigonometria:
    delta_x = delta_s * cos(delta_tita + tita)
    delta_y = delta_s * sin(delta_tita + tita)

    #obtengo posicion actual:
    x_nuevo = x + delta_x
    y_nuevo = y + delta_y
    tita_nuevo = ((tita + delta_tita + pi) % (2*pi)) - pi #Convierto la suma de los titas a un valor entre [-pi,pi]
    #Guardo el nuevo valor en historico
    historico.append({"x":x_nuevo,"y":y_nuevo,"tita":tita_nuevo,"tipo":tipo})
    #Determino la posicion actual:
    x = x_nuevo
    y = y_nuevo
    tita = tita_nuevo
    print("Nuevos valores de posicion (x, y, tita):", round(x,2), round(y,2), round(tita*180/pi,1),"\n")
#####

# Lectura de entrada:
def leerEntrada(ingreso):
    valor=0

    if(ingreso=="d"): #d- drive, avanza       
        print("Cuantos mm quieres avanzar?")
        valor = input()
        try:
            [delta_s, delta_tita] = desplazarse(valor) 
            cargar_odometria(delta_s, delta_tita,"Avanzar")
        except Exception as e:
            print("Ocurrio un error:", e)

    elif(ingreso=="r"): #retroceder
        print("Cuantos mm quieres retroceder?")
        valor = input()
        try:
            [delta_s, delta_tita] = desplazarse(valor, retrocedo=1)
            cargar_odometria(delta_s, delta_tita,"Retroceder") 
        except Exception as e:
            print("Ocurrio un error:", e)

    elif(ingreso=="gi"): #girar hacia la izquierda
        print("Cuantos grados quieres girar hacia la izquierda?")
        valor = input()
        try:
            [delta_s, delta_tita] = girar(valor, haciaDerecha=0)
            cargar_odometria(delta_s, delta_tita,"Giro izq.")
        except Exception as e:
            print("Ocurrio un error:", e)

    elif(ingreso=="gd"): #girar hacia la derecha
        print("Cuantos grados quieres girar hacia la derecha?")
        valor = input()
        try:
            [delta_s, delta_tita] = girar(valor, haciaDerecha=1)
            cargar_odometria(delta_s, delta_tita,"Giro der.")
        except Exception as e:
            print("Ocurrio un error:", e)
    elif(ingreso=="obj"): #moverse hacia objetivo (tarea autonoma)
        try:
            print("Ingresa coordenadas (x,y) a donde quieres ir")
            x_obj = input("ingresa coordenada x:")
            y_obj = input("ingresa coordenada y:")
            ir_coordenadas(x_obj,y_obj)
        except Exception as e:
            print("Ocurrio un error:", e)
    elif(ingreso=="c"): #realizo un movimiento de un cuadrado (tarea autonoma)
        try:
            print("Ingresa tamano de cuadrado")
            tamano = input("ingresa tamano (en mm):")
            moverse_cuadrado(tamano)
        except Exception as e:
            print("Ocurrio un error:", e)
    elif(ingreso=="o"): #muestra de odometria
        mostrar_odometria()
#####

# Bucle principal del programa #
x = y = tita = 0 #Variables globales
historico = []
while True:

    print("\nInstrucciones: \n 'd':Avanzar (drive), 'r': Retroceder,\n 'gd': Girar hacia derecha, 'gi': Girar hacia izquierda")
    print("'obj': Moverse hacia un objetivo, 'c': Realizar el movimiento en un cuadrado")
    print("Para odometia ingrese 'o'")
    direction = input("Ingrese una accion: ")
    leerEntrada(direction)
