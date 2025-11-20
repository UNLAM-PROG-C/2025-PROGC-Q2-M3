"""
Constantes para el juego Batalla Naval - SERVIDOR
Archivo de constantes específicas para el servidor sin dependencias de pygame
"""

import os

# === CONFIGURACIÓN DE RED ===
DEFAULT_SERVER_HOST = "localhost"
DEFAULT_SERVER_PORT = 8888
DEFAULT_HOST_ALL_INTERFACES = "0.0.0.0"
DEFAULT_HOST_LOCALHOST = "localhost"
DEFAULT_HOST_LOOPBACK = "127.0.0.1"
NETWORK_BUFFER_SIZE = 1024
NETWORK_TIMEOUT = 1.0

# Timeouts y límites del servidor
SERVER_READ_TIMEOUT = 1.0
SERVER_CLOSE_TIMEOUT = 5
JSON_DECODE_MAX_RETRIES = 3
CONNECTION_CHECK_INTERVAL = 1.0

# === CONFIGURACIÓN DE JUEGO ===
# Tablero de juego
GRID_SIZE = 10
CELL_MARGIN = 2

# Configuración de barcos
SHIP_SIZES = [5, 4, 3, 3, 2]
SHIP_NAMES = {
    5: "Portaaviones",
    4: "Destructor Acorazado", 
    3: "Barco de Ataque",
    2: "Lancha Rapida"
}

# Estados de celda
CELL_EMPTY = 0
CELL_SHIP = 1
CELL_HIT = 2
CELL_WATER_HIT = 3

# Máximo de jugadores
MAX_PLAYERS = 2

# === CONFIGURACIÓN DE VALIDACIÓN ===
# Límites de entrada
MIN_PORT_NUMBER = 1
MAX_PORT_NUMBER = 65535
MIN_COORDINATE = 0
MAX_COORDINATE = 9

# === CONFIGURACIÓN DE MENSAJES ===
# Límites de caracteres para mensajes
MESSAGE_TYPE_MAX_LENGTH = 50
ERROR_MESSAGE_MAX_LENGTH = 200
PLAYER_ID_LENGTH = 8

# UUID
UUID_SHORT_LENGTH = 8

# === CONFIGURACIÓN DE LOGGING ===
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# === CONFIGURACIÓN DE DESARROLLO ===
# Flags de debug
DEBUG_NETWORK = False
DEBUG_GAME_STATE = False

# === CONFIGURACIÓN DE SERVIDOR (start_server.py) ===
# Constantes para eliminación de números mágicos
BANNER_WIDTH = 80
FIREWALL_TCP_PROTOCOL = '/tcp'
MAX_METHOD_LINES = 15
ARG_VALIDATION_EXIT_SUCCESS = 0
ARG_VALIDATION_EXIT_ERROR = 1
USER_INPUT_YES = 's'
USER_INPUT_NO = 'n'

# === CONFIGURACIÓN DE PLAYER ===
# Constantes para la clase Player
UTF8_ENCODING = 'utf-8'
JSON_MESSAGE_DELIMITER = '\n'
SHOT_RESULT_HIT = 'hit'
SHOT_RESULT_MISS = 'miss'
SHOT_RESULT_SUNK = 'sunk'

# Resultados de disparos
SHOT_RESULTS = {
    'HIT': 'hit',
    'MISS': 'miss',
    'SUNK': 'sunk'
}

# === CONFIGURACIÓN DE BATTLESHIP SERVER ===
# Constantes para la clase BattleshipServer
LOCALHOST_HOST = "localhost"
CONNECTION_ERROR_MESSAGES = {
    'SERVER_FULL': "Servidor lleno. Máximo 2 jugadores.",
    'NOT_YOUR_TURN': 'No es tu turno',
    'SHIPS_PLACEMENT_ERROR': 'Error colocando barcos',
    'OPPONENT_DISCONNECTED': 'Tu oponente se ha desconectado'
}
GAME_MESSAGES = {
    'GAME_STARTED': 'El juego ha comenzado - Pantalla de juego activa',
    'WINNER': '¡Ganaste!',
    'LOSER': 'Perdiste'
}

# === CONFIGURACIÓN DE SHIP ===
# Constantes para la clase Ship
SHIP_POSITION_NOT_HIT_THRESHOLD = 0
SHIP_INITIAL_HITS = 0
SHIP_ORIENTATION_HORIZONTAL = True
SHIP_ORIENTATION_VERTICAL = False
ERROR_MESSAGES_SHIP = {
    'EMPTY_POSITIONS': "Las posiciones no pueden estar vacías",
    'MISSING_INIT_PARAMS': "Debe proporcionar 'size' o 'positions' para inicializar el barco"
}

# === CONFIGURACIÓN DE NETWORK MANAGER ===
# Constantes para la clase NetworkManager
THREAD_DAEMON_MODE = True
NETWORK_ENCODING = 'utf-8'
MESSAGE_BUFFER_SPLIT_LIMIT = 1
MESSAGE_TYPES = {
    'PLAYER_CONNECT': 'player_connect',
    'PLAYERS_READY': 'players_ready',
    'GAME_START': 'game_start',
    'GAME_UPDATE': 'game_update',
    'SHOT_RESULT': 'shot_result',
    'GAME_OVER': 'game_over',
    'PLAYER_DISCONNECT': 'player_disconnect',
    'ERROR': 'error',
    'PLACE_SHIPS': 'place_ships',
    'SHOT': 'shot',
    'START_GAME': 'start_game'
}
NETWORK_LOG_MESSAGES = {
    'NOT_CONNECTED': "❌ No conectado al servidor",
    'SEND_SUCCESS': "✅ Mensaje enviado exitosamente",
    'SERVER_DISCONNECTED': "🔌 Error: Servidor desconectado durante envío",
    'NO_DATA_RECEIVED': "🔌 Servidor desconectado - No se recibieron más datos",
    'CONNECTION_RESET': "🔌 Servidor desconectado - Conexión resetteada/abortada",
    'NOTIFYING_DISCONNECT': "📞 Notificando desconexión del servidor",
    'NO_DISCONNECT_CALLBACK': "⚠️ No hay callback configurado para server_disconnect",
    'NO_GAME_START_CALLBACK': "⚠️ No hay callback configurado para game_start",
    'NO_PLAYER_DISCONNECT_CALLBACK': "⚠️ No hay callback configurado para player_disconnect",
    'UNKNOWN_PLAYER': 'desconocido',
    'DEFAULT_DISCONNECT_MESSAGE': 'Jugador desconectado',
    'DEFAULT_ERROR_MESSAGE': 'Error desconocido',
    'NO_CONNECTION': "❌ ERROR: No hay conexión al servidor"
}

# === CONFIGURACIÓN DE TIEMPO ===
# Delays y timeouts
ANIMATION_FRAME_TIME = 16  # ~60 FPS

# === FASES DEL JUEGO ===
GAME_PHASE_PLACEMENT = "placement"
GAME_PHASE_WAITING_BATTLE = "waiting_for_battle"
GAME_PHASE_BATTLE = "battle"

# === CONFIGURACIÓN DE BARCOS ===
DEFAULT_SHIP_SIZE = 2
SHIP_HORIZONTAL_DEFAULT = True
SHIP_VERTICAL = False
INITIAL_SHIP_INDEX = 0

# Configuración de barcos esperados
EXPECTED_ENEMY_SHIPS = [
    {"name": "Portaaviones", "size": 5, "sunk": False},
    {"name": "Destructor Acorazado", "size": 4, "sunk": False},
    {"name": "Barco de Ataque #1", "size": 3, "sunk": False},
    {"name": "Barco de Ataque #2", "size": 3, "sunk": False},
    {"name": "Lancha Rapida", "size": 2, "sunk": False}
]

# === CONFIGURACIÓN DEL TABLERO ===
BOARD_SIZE_DEFAULT = 450

# === TEXTOS DEL SERVIDOR ===
SERVER_TEXT = {
    'GAME_STARTED': 'El juego ha comenzado - Pantalla de juego activa',
    'WINNER': '¡Ganaste!',
    'LOSER': 'Perdiste',
    'SHIPS_SENT': "Barcos enviados al servidor",
    'BATTLE_START': "🚀 Iniciando fase de batalla...",
    'SUNK_ENEMY_SHIP': "🎯 ¡HUNDISTE EL {} ENEMIGO!",
    'ENEMY_SUNK_MY_SHIP': "💥 ¡El enemigo hundió tu {}!",
    'GAME_RESET': "🔄 Estado del juego reseteado para nueva partida"
}

# === CONFIGURACIÓN DE ESTADO DEL SERVIDOR ===
# Estados de los jugadores
PLAYER_STATE_CONNECTED = "connected"
PLAYER_STATE_READY = "ready"
PLAYER_STATE_PLAYING = "playing"
PLAYER_STATE_DISCONNECTED = "disconnected"

# Estados del juego
GAME_STATE_WAITING_PLAYERS = "waiting_players"
GAME_STATE_PLACEMENT = "placement"
GAME_STATE_BATTLE = "battle"
GAME_STATE_FINISHED = "finished"