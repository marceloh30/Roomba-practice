import pycreate2
from matplotlib import pyplot as plt
import time
import pycreate2.createSerial

if __name__ == "__main__":
    # Create a Create2 Bot
    port = 'COM5'
    baud = {
        'default': 115200,
        'alt': 19200  # shouldn't need this unless you accidentally set it to this
    }
    

    bot = pycreate2.Create2(port=port, baud=baud['default'])
    
    bot.start()
    bot.safe()

historicoEncoders = {"izq":[],"der":[],"time":[]}
bot.drive_direct(-300,300)
i=0
while ( len(historicoEncoders["izq"]) < 300):
    sensores = bot.get_sensors()
    historicoEncoders["izq"].append(sensores.encoder_counts_left)
    historicoEncoders["der"].append(sensores.encoder_counts_right)
    historicoEncoders["time"].append(time.time())
    time.sleep(0.01)



bot.drive_stop()

tiempos = historicoEncoders["time"]
encoderIzq = historicoEncoders["izq"]
encoderDer = historicoEncoders["der"]
print(tiempos)
print(encoderDer)
print(encoderIzq)
plt.title("Respuesta de ejes en el tiempo") 
plt.xlabel("Cuentas Encoder izq") 
plt.ylabel("Tiempo (seg)") 
plt.plot(tiempos,encoderIzq) 
#plt.xlabel("Cuentas Encoder der") 
#plt.plot(tiempos,encoderDer) 
plt.show()