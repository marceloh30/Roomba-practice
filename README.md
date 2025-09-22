# Control de iRobot Roomba con Python

Este repositorio contiene scripts de Python para controlar un robot iRobot Roomba 650 (o Create 2). Incluye scripts para control autónomo por comandos, control manual por teclado y herramientas de análisis.

## Requisitos

* **Librerías**: `pycreate2`, `pynput`, `matplotlib`
    ```bash
    pip install pycreate2 pynput matplotlib
    ```
* **Hardware**: Robot iRobot Create 2 / Roomba 650 y un cable de comunicación serie.

## Scripts Principales

* **`practica.py`**: Controla el robot mediante comandos en la consola para realizar movimientos autónomos. Permite avanzar, retroceder, girar y moverse a coordenadas específicas. Mantiene un registro de la posición del robot mediante odometría.
* **`movimientoTeclado.py`**: Permite el control manual del robot en tiempo real usando las flechas del teclado. La tecla `Esc` detiene el programa y el robot.

## Scripts de Análisis (`analysis/`)

* **`respuestaEncoder.py`**: Es un script de diagnóstico que hace girar al robot, lee los datos de sus encoders y luego los grafica usando `matplotlib`.
* **`pruebaLogica.py`**: Una versión de simulación que prueba la lógica de odometría y movimiento sin necesidad de conectar el robot real. La función `actuar` está alterada para pruebas y no se comunica con el hardware.

## Cómo Usar

1.  **Instala las librerías** con el comando `pip` mostrado arriba.
2.  **Edita el script** que quieras usar y cambia la variable `port` al puerto COM correcto (ej: `'COM5'`).
3.  **Ejecuta** el script desde tu terminal:
    ```bash
    python nombre_del_script.py
    ```
