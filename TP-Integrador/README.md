# Batalla Naval

Un juego de Batalla Naval implementado en Python con soporte multijugador en tiempo real utilizando sockets asíncronos.

## Requisitos del Sistema

- Python 3.7 o superior
- Pygame
- Sistema operativo Windows

## Instalación y Ejecución Local

### Paso 1: Clonar el Repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd 2025-PROGC-Q2-M3/TP-Integrador
```

### Paso 2: Iniciar el Servidor

1. Navega hasta la carpeta del servidor:
   ```bash
   cd server
   ```

2. Ejecuta el servidor utilizando el archivo batch:
   ```bash
   run_server.bat
   ```

El servidor se iniciará en `localhost:8888` y estará esperando conexiones de los jugadores.

### Paso 3: Ejecutar el Juego

1. Abre una nueva terminal y navega hasta la carpeta del juego:
   ```bash
   cd game
   ```

2. Ejecuta el cliente del juego:
   ```bash
   BatallaNaval.bat
   ```

3. El juego se abrirá y se conectará automáticamente al servidor local.

### Paso 4: Jugar

1. Necesitas dos instancias del juego ejecutándose para poder jugar (dos ventanas del juego)
2. Una vez que ambos jugadores estén conectados, pueden hacer clic en "Iniciar Juego"
3. Coloca tus barcos en el tablero
4. Cuando ambos jugadores hayan terminado de colocar sus barcos, comenzará la fase de batalla
5. Haz clic en el tablero enemigo para disparar durante tu turno

## Estructura del Proyecto

```
TP-Integrador/
├── server/                 # Código del servidor
│   ├── server.py          # Archivo principal del servidor
│   ├── run_server.bat     # Script para ejecutar el servidor
│   └── classes/           # Clases del servidor
├── game/                  # Código del cliente/juego
│   ├── main.py           # Archivo principal del juego
│   ├── BatallaNaval.bat  # Script para ejecutar el juego
│   ├── assets/           # Recursos (imágenes, sonidos)
│   └── classes/          # Clases del juego
└── README.md             # Este archivo
```

## Notas Técnicas

- El servidor utiliza programación asíncrona con asyncio para manejar múltiples conexiones
- La comunicación entre cliente y servidor se realiza mediante mensajes JSON
- El juego incluye validación automática de posicionamiento de barcos
- Sistema robusto de detección de desconexiones y reconexiones

## Solución de Problemas

- **Error de conexión**: Asegúrate de que el servidor esté ejecutándose antes de iniciar el cliente
- **Archivos faltantes**: Verifica que todas las carpetas `assets` contengan los recursos necesarios
- **Puerto ocupado**: Si el puerto 8888 está en uso, el servidor mostrará un error. Cierra otras aplicaciones que puedan estar usando ese puerto