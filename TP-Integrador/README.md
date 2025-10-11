# Batalla Naval - Cliente

## Descripción
Juego de batalla naval multijugador implementado con Pygame y sockets. Este es el cliente del juego que permite a los jugadores conectarse a un servidor y jugar contra otro jugador.

## Características
- Interfaz gráfica con Pygame
- Menú principal con opciones de conexión
- Tablero personal para colocar barcos
- Tablero enemigo para realizar disparos
- Sistema de red preparado para comunicación con servidor
- Soporte para diferentes tamaños de barcos

## Estructura del Proyecto
```
TP-Integrador/
├── main.py           # Archivo principal del cliente
├── menu.py           # Pantalla del menú principal
├── game.py           # Lógica principal del juego y tableros
├── network.py        # Manejo de comunicación de red
├── utils.py          # Utilidades y funciones auxiliares
├── requirements.txt  # Dependencias del proyecto
├── README.md         # Este archivo
└── assets/
    └── images/
        ├── menu.png         # Imagen de fondo del menú
        ├── background.png   # Imagen de fondo del juego
        ├── barcode2.png     # Imagen de barco tamaño 2
        ├── barcode3.png     # Imagen de barco tamaño 3
        ├── barcode32.png    # Imagen de barco tamaño 3 (alternativo)
        ├── barcode4.png     # Imagen de barco tamaño 4
        └── barcode5.png     # Imagen de barco tamaño 5
```

## Instalación

1. Asegúrate de tener Python 3.7+ instalado
2. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

## Cómo jugar

### Ejecutar el cliente:
```
python main.py
```

### Controles del juego:

#### En el menú:
- **Conectar a Servidor**: Intenta conectarse al servidor (localhost:8888 por defecto)
- **Iniciar Partida**: Se habilita cuando hay 2 jugadores conectados

#### Durante la colocación de barcos:
- **Click izquierdo**: Colocar barco en la posición del mouse
- **Click derecho** o **tecla R**: Rotar barco entre horizontal y vertical
- **Preview visual**: Verde si se puede colocar, rojo si no es posible

#### Durante la batalla:
- **Click izquierdo en tablero enemigo**: Realizar disparo
- Los disparos se marcan como impacto (círculo rojo) o falla (círculo blanco)

## Barcos a colocar
El juego incluye los siguientes barcos que deben colocarse:
- 1 barco de 5 casillas
- 1 barco de 4 casillas  
- 2 barcos de 3 casillas
- 1 barco de 2 casillas

## Estados del juego
1. **Menú**: Pantalla inicial con opciones de conexión
2. **Esperando**: Conectado al servidor, esperando segundo jugador
3. **Colocación**: Colocar barcos en el tablero personal
4. **Batalla**: Turnos para disparar al tablero enemigo

## Configuración de red
Por defecto, el cliente intenta conectarse a:
- **Host**: localhost
- **Puerto**: 8888

Estos valores pueden modificarse en el archivo `network.py` en la clase `NetworkManager`.

## Servidor incluido
El proyecto ahora incluye un servidor completo implementado con `asyncio`:

### Características del servidor:
- **Máximo 2 jugadores**: Solo permite 2 conexiones simultáneas
- **Comunicación asíncrona**: Usa `async/await` para manejar múltiples clientes
- **Fases del juego**: Maneja colocación de barcos y batalla automáticamente
- **Validación**: Verifica disparos y detecta barcos hundidos
- **Turnos**: Alterna turnos entre jugadores automáticamente

### Cómo ejecutar el servidor:
```bash
python server.py
```

O usa el script:
```bash
run_server.bat
```

### Protocolo de comunicación:
El servidor y cliente se comunican usando mensajes JSON que incluyen:
- Conexión y asignación de ID de jugador
- Estado de jugadores conectados (habilita botón "Iniciar Partida")
- Colocación de barcos
- Disparos y resultados
- Cambio de turnos
- Fin del juego

## Cómo jugar multijugador:

### Método 1: Manual
1. **Iniciar el servidor**:
   ```bash
   python server.py
   ```
   O hacer doble-click en `test_server.bat`

2. **Ejecutar primer cliente**:
   ```bash
   python main.py  
   ```
   O hacer doble-click en `test_client.bat`
   - Hacer click en "Conectar a Servidor"

3. **Ejecutar segundo cliente** (en otra terminal/ventana):
   ```bash
   python main.py
   ```
   - Hacer click en "Conectar a Servidor"

4. **Iniciar partida**:
   - Cuando ambos clientes estén conectados, el botón "Iniciar Partida" se habilitará ✅
   - **Cualquier jugador puede hacer click** → ¡Ambos se redirigen automáticamente! 🎮

### Método 2: Prueba automática
```bash
python test_full_flow.py
```

5. **Colocar barcos**:
   - Cada jugador coloca sus barcos en su tablero
   - El juego continúa automáticamente cuando ambos terminen

6. **Batalla**:
   - Los turnos se alternan automáticamente
   - Hacer click en el tablero enemigo para disparar
   - El servidor valida y notifica los resultados

## Pantalla de juego mejorada:

La interfaz de juego ahora incluye:
- **Fondo personalizado**: Usa la imagen `background.png` o un degradado azul océano
- **Dos tableros claramente diferenciados**:
  - Tablero izquierdo: "MI FLOTA" (azul) - para colocar tus barcos
  - Tablero derecho: "TABLERO ENEMIGO" (rojo) - para atacar
- **Paneles semi-transparentes** que enmarcan cada tablero
- **Coordenadas mejoradas** (A-J, 1-10) con fondos decorativos
- **Grid profesional** con líneas más gruesas cada 5 casillas
- **Efecto tablero** con celdas alternadas para mejor visualización
- **Panel de información** en la parte inferior con estado del juego
- **Título principal** "BATALLA NAVAL" con efectos de sombra

### Archivo de prueba:
```bash
python test_game.py
```
Este archivo permite probar solo la interfaz visual sin necesidad del servidor.

## Notas importantes
- El servidor debe estar ejecutándose antes de conectar los clientes
- Solo se permiten exactamente 2 jugadores por partida
- Las imágenes en assets/images/ son opcionales, el juego funciona con colores si no están disponibles
- El servidor maneja toda la lógica del juego, los clientes solo muestran la interfaz