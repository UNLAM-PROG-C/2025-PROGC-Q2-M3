"""Módulo del gestor de red para el juego Batalla Naval.

Este módulo contiene la implementación del NetworkManager que maneja
la comunicación bidireccional con el servidor de Batalla Naval.
"""

import socket
import json
import threading
import sys
import os
from typing import Optional, Callable, Any, Dict

# Importar constants desde la carpeta del cliente
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from constants import (DEFAULT_SERVER_HOST, DEFAULT_SERVER_PORT, NETWORK_BUFFER_SIZE, 
                      THREAD_DAEMON_MODE, NETWORK_ENCODING, MESSAGE_BUFFER_SPLIT_LIMIT,
                      MESSAGE_TYPES, NETWORK_LOG_MESSAGES, JSON_MESSAGE_DELIMITER)

class NetworkManager:
    """Gestor de comunicaciones de red para el cliente de Batalla Naval.
    
    Esta clase maneja toda la comunicación bidireccional con el servidor,
    incluyendo conexión, envío de mensajes, recepción de respuestas y
    gestión de callbacks para eventos del servidor.
    
    Attributes:
        socket (Optional[socket.socket]): Socket de conexión con el servidor.
        connected (bool): Estado de conexión con el servidor.
        server_host (str): Dirección IP del servidor.
        server_port (int): Puerto del servidor.
        player_id (Optional[str]): ID único del jugador asignado por el servidor.
        receive_thread (threading.Thread): Hilo para recepción de mensajes.
        on_players_ready (Optional[Callable]): Callback para estado de jugadores.
        on_game_start (Optional[Callable]): Callback para inicio de juego.
        on_game_update (Optional[Callable]): Callback para actualizaciones.
        on_shot_result (Optional[Callable]): Callback para resultados de disparos.
        on_game_over (Optional[Callable]): Callback para fin de juego.
        on_server_disconnect (Optional[Callable]): Callback para desconexión.
    """
    def __init__(self):
        """Inicializar el gestor de red con valores por defecto."""
        self._initialize_connection_attributes()
        self._initialize_server_config()
        self._initialize_callbacks()
        
    def _initialize_connection_attributes(self) -> None:
        """Inicializar atributos de conexión."""
        self.socket: Optional[socket.socket] = None
        self.connected: bool = False
        self.player_id: Optional[str] = None
        
    def _initialize_server_config(self) -> None:
        """Inicializar configuración del servidor."""
        self.server_host: str = DEFAULT_SERVER_HOST
        self.server_port: int = DEFAULT_SERVER_PORT
        
    def _initialize_callbacks(self) -> None:
        """Inicializar callbacks para eventos del servidor."""
        self.on_players_ready: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_game_start: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_game_update: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_shot_result: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_game_over: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_server_disconnect: Optional[Callable[[], None]] = None
    def connect_to_server(self, host: Optional[str] = None, port: Optional[int] = None) -> bool:
        """Intentar conectar al servidor.
        
        Args:
            host (Optional[str]): Dirección del servidor. Si es None, usa el valor por defecto.
            port (Optional[int]): Puerto del servidor. Si es None, usa el valor por defecto.
            
        Returns:
            bool: True si la conexión fue exitosa, False en caso contrario.
        """
        self._update_server_config(host, port)
        
        try:
            return self._establish_connection()
        except Exception as e:
            print(f"Error conectando al servidor: {e}")
            self.connected = False
            return False
            
    def _update_server_config(self, host: Optional[str], port: Optional[int]) -> None:
        """Actualizar configuración del servidor.
        
        Args:
            host (Optional[str]): Nueva dirección del servidor.
            port (Optional[int]): Nuevo puerto del servidor.
        """
        if host:
            self.server_host = host
        if port:
            self.server_port = port
            
    def _establish_connection(self) -> bool:
        """Establecer conexión con el servidor.
        
        Returns:
            bool: True si la conexión fue exitosa, False en caso contrario.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.server_host, self.server_port))
        self.connected = True
        
        self._start_receive_thread()
        return True
        
    def _start_receive_thread(self) -> None:
        """Iniciar hilo para recibir mensajes del servidor."""
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.daemon = THREAD_DAEMON_MODE
        self.receive_thread.start()
    def disconnect(self) -> None:
        """Desconectar del servidor y limpiar recursos."""
        if self.socket:
            self.connected = False
            self.socket.close()
            self.socket = None
    def send_message(self, message_type: str, data: Optional[Dict[str, Any]] = None) -> bool:
        """Enviar mensaje al servidor.
        
        Args:
            message_type (str): Tipo de mensaje a enviar.
            data (Optional[Dict[str, Any]]): Datos adicionales del mensaje.
            
        Returns:
            bool: True si el mensaje fue enviado exitosamente, False en caso contrario.
        """
        if not self.connected:
            print(NETWORK_LOG_MESSAGES['NOT_CONNECTED'])
            return False
            
        try:
            message = self._create_message(message_type, data)
            return self._send_raw_message(message)
        except (ConnectionResetError, ConnectionAbortedError):
            return self._handle_connection_error()
        except Exception as e:
            print(f"❌ Error enviando mensaje: {e}")
            return False
            
    def _create_message(self, message_type: str, data: Optional[Dict[str, Any]]) -> str:
        """Crear mensaje en formato JSON.
        
        Args:
            message_type (str): Tipo del mensaje.
            data (Optional[Dict[str, Any]]): Datos del mensaje.
            
        Returns:
            str: Mensaje JSON formateado.
        """
        message = {
            'type': message_type,
            'player_id': self.player_id,
            'data': data
        }
        return json.dumps(message) + JSON_MESSAGE_DELIMITER
        
    def _send_raw_message(self, message_json: str) -> bool:
        """Enviar mensaje JSON crudo al servidor.
        
        Args:
            message_json (str): Mensaje JSON a enviar.
            
        Returns:
            bool: True si fue enviado exitosamente, False en caso contrario.
        """
        print(f"📤 Enviando mensaje al servidor: {message_json.strip()}")
        self.socket.send(message_json.encode(NETWORK_ENCODING))
        print(NETWORK_LOG_MESSAGES['SEND_SUCCESS'])
        return True
        
    def _handle_connection_error(self) -> bool:
        """Manejar error de conexión durante envío.
        
        Returns:
            bool: Siempre retorna False.
        """
        print(NETWORK_LOG_MESSAGES['SERVER_DISCONNECTED'])
        self.connected = False
        if self.on_server_disconnect:
            self.on_server_disconnect()
        return False
    
    def receive_messages(self) -> None:
        """Bucle para recibir mensajes del servidor en un hilo separado."""
        buffer: str = ""
        
        while self.connected:
            buffer = self._process_incoming_data(buffer)
            
    def _process_incoming_data(self, buffer: str) -> str:
        """Procesar datos entrantes del servidor.
        
        Args:
            buffer (str): Buffer de datos acumulados.
            
        Returns:
            str: Buffer actualizado después del procesamiento.
        """
        try:
            data = self._receive_server_data()
            if not data:
                return buffer
                
            buffer += data
            return self._process_message_buffer(buffer)
            
        except Exception as e:
            self._handle_receive_error(e)
            return buffer
            
    def _receive_server_data(self) -> str:
        """Recibir datos del servidor.
        
        Returns:
            str: Datos recibidos decodificados, o cadena vacía si no hay datos.
        """
        try:
            data = self.socket.recv(NETWORK_BUFFER_SIZE)
            if not data:
                self._handle_server_disconnection()
                return ""
                
            return data.decode(NETWORK_ENCODING)
            
        except (ConnectionResetError, ConnectionAbortedError):
            self._handle_server_disconnection_error()
            return ""
            
    def _handle_server_disconnection(self) -> None:
        """Manejar desconexión normal del servidor."""
        print(NETWORK_LOG_MESSAGES['NO_DATA_RECEIVED'])
        self.connected = False
        if self.on_server_disconnect:
            print(NETWORK_LOG_MESSAGES['NOTIFYING_DISCONNECT'])
            self.on_server_disconnect()
            
    def _handle_server_disconnection_error(self) -> None:
        """Manejar desconexión por error de conexión."""
        print(NETWORK_LOG_MESSAGES['CONNECTION_RESET'])
        self.connected = False
        if self.on_server_disconnect:
            self.on_server_disconnect()
            
    def _process_message_buffer(self, buffer: str) -> str:
        """Procesar buffer de mensajes para extraer mensajes completos.
        
        Args:
            buffer (str): Buffer con mensajes potencialmente incompletos.
            
        Returns:
            str: Buffer restante después del procesamiento.
        """
        while JSON_MESSAGE_DELIMITER in buffer:
            message, buffer = buffer.split(JSON_MESSAGE_DELIMITER, MESSAGE_BUFFER_SPLIT_LIMIT)
            if message.strip():
                self._handle_complete_message(message)
        return buffer
        
    def _handle_complete_message(self, message: str) -> None:
        """Manejar un mensaje completo del servidor.
        
        Args:
            message (str): Mensaje completo recibido.
        """
        print(f"📥 Mensaje recibido del servidor: {message}")
        try:
            parsed_message = json.loads(message)
            self.handle_server_message(parsed_message)
        except json.JSONDecodeError as e:
            print(f"{NETWORK_LOG_MESSAGES['PARSING_ERROR']}: {e}")
            
    def _handle_receive_error(self, error: Exception) -> None:
        """Manejar errores durante la recepción de mensajes.
        
        Args:
            error (Exception): Excepción ocurrida durante la recepción.
        """
        print(f"❌ Error recibiendo mensaje: {error}")
        
        self.connected = False
        if self.on_server_disconnect:
            self.on_server_disconnect()
    
    def handle_server_message(self, message: Dict[str, Any]) -> None:
        """Manejar mensajes recibidos del servidor.
        
        Args:
            message (Dict[str, Any]): Mensaje parseado del servidor.
        """
        message_type = message.get('type')
        data = message.get('data', {})
        
        handler_map = {
            MESSAGE_TYPES['PLAYER_CONNECT']: self._handle_player_connect,
            MESSAGE_TYPES['PLAYERS_READY']: self._handle_players_ready,
            MESSAGE_TYPES['GAME_START']: self._handle_game_start,
            MESSAGE_TYPES['GAME_UPDATE']: self._handle_game_update,
            MESSAGE_TYPES['SHOT_RESULT']: self._handle_shot_result,
            MESSAGE_TYPES['GAME_OVER']: self._handle_game_over,
            MESSAGE_TYPES['PLAYER_DISCONNECT']: self._handle_player_disconnect,
            MESSAGE_TYPES['ERROR']: self._handle_error
        }
        
        handler = handler_map.get(message_type)
        if handler:
            handler(data)
        else:
            print(f"Tipo de mensaje desconocido: {message_type}")
            
    def _handle_player_connect(self, data: Dict[str, Any]) -> None:
        """Manejar mensaje de conexión de jugador.
        
        Args:
            data (Dict[str, Any]): Datos del mensaje.
        """
        self.player_id = data.get('player_id')
        print(f"ID de jugador asignado: {self.player_id}")
        
    def _handle_players_ready(self, data: Dict[str, Any]) -> None:
        """Manejar mensaje de estado de jugadores.
        
        Args:
            data (Dict[str, Any]): Datos del mensaje.
        """
        if self.on_players_ready:
            self.on_players_ready(data)
            
    def _handle_game_start(self, data: Dict[str, Any]) -> None:
        """Manejar mensaje de inicio de juego.
        
        Args:
            data (Dict[str, Any]): Datos del mensaje.
        """
        print(f"🎮 Mensaje GAME_START recibido del servidor: {data}")
        if self.on_game_start:
            print("📞 Llamando callback on_game_start")
            self.on_game_start(data)
        else:
            print(NETWORK_LOG_MESSAGES['NO_GAME_START_CALLBACK'])
            
    def _handle_game_update(self, data: Dict[str, Any]) -> None:
        """Manejar mensaje de actualización de juego.
        
        Args:
            data (Dict[str, Any]): Datos del mensaje.
        """
        if self.on_game_update:
            self.on_game_update(data)
            
    def _handle_shot_result(self, data: Dict[str, Any]) -> None:
        """Manejar mensaje de resultado de disparo.
        
        Args:
            data (Dict[str, Any]): Datos del mensaje.
        """
        if self.on_shot_result:
            self.on_shot_result(data)
            
    def _handle_game_over(self, data: Dict[str, Any]) -> None:
        """Manejar mensaje de fin de juego.
        
        Args:
            data (Dict[str, Any]): Datos del mensaje.
        """
        if self.on_game_over:
            self.on_game_over(data)
            
    def _handle_player_disconnect(self, data: Dict[str, Any]) -> None:
        """Manejar mensaje de desconexión de jugador.
        
        Args:
            data (Dict[str, Any]): Datos del mensaje.
        """
        print(f"🔌 MENSAJE PLAYER_DISCONNECT RECIBIDO: {data}")
        disconnected_player = data.get('disconnected_player', NETWORK_LOG_MESSAGES['UNKNOWN_PLAYER'])
        message = data.get('message', NETWORK_LOG_MESSAGES['DEFAULT_DISCONNECT_MESSAGE'])
        print(f"🔌 {message} (Jugador: {disconnected_player})")
        
        if self.on_server_disconnect:
            print("📞 Llamando callback de desconexión por jugador desconectado")
            self.on_server_disconnect()
        else:
            print(NETWORK_LOG_MESSAGES['NO_PLAYER_DISCONNECT_CALLBACK'])
            
    def _handle_error(self, data: Dict[str, Any]) -> None:
        """Manejar mensaje de error del servidor.
        
        Args:
            data (Dict[str, Any]): Datos del mensaje.
        """
        error_msg = data.get('error', NETWORK_LOG_MESSAGES['DEFAULT_ERROR_MESSAGE'])
        print(f"Error del servidor: {error_msg}")
    
    def place_ships(self, ship_positions: Dict[str, Any]) -> bool:
        """Enviar posiciones de los barcos al servidor.
        
        Args:
            ship_positions (Dict[str, Any]): Posiciones de los barcos.
            
        Returns:
            bool: True si fue enviado exitosamente, False en caso contrario.
        """
        return self.send_message(MESSAGE_TYPES['PLACE_SHIPS'], {'ships': ship_positions})
    
    def make_shot(self, x: int, y: int) -> bool:
        """Enviar un disparo al servidor.
        
        Args:
            x (int): Coordenada X del disparo.
            y (int): Coordenada Y del disparo.
            
        Returns:
            bool: True si fue enviado exitosamente, False en caso contrario.
        """
        return self.send_message(MESSAGE_TYPES['SHOT'], {'x': x, 'y': y})
    
    def start_game(self) -> bool:
        """Solicitar inicio del juego al servidor.
        
        Returns:
            bool: True si la solicitud fue enviada exitosamente, False en caso contrario.
        """
        self._log_start_game_info()
        
        if not self._validate_connection():
            return False
            
        result = self.send_message(MESSAGE_TYPES['START_GAME'], {})
        print(f"📤 Resultado del envío de start_game: {result}")
        return result
        
    def _log_start_game_info(self) -> None:
        """Registrar información sobre el inicio del juego."""
        print("🚀 INICIANDO: Enviando solicitud de inicio de juego al servidor")
        print(f"🔌 Estado de conexión: {self.connected}")
        print(f"🆔 ID del jugador: {self.player_id}")
        
    def _validate_connection(self) -> bool:
        """Validar que existe conexión con el servidor.
        
        Returns:
            bool: True si hay conexión, False en caso contrario.
        """
        if not self.connected:
            print(NETWORK_LOG_MESSAGES['NO_CONNECTION'])
            return False
        return True
    
    def set_players_ready_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Establecer callback para cuando cambie el estado de jugadores.
        
        Args:
            callback (Callable[[Dict[str, Any]], None]): Función a llamar cuando cambie el estado.
        """
        self.on_players_ready = callback
    
    def set_game_start_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Establecer callback para cuando inicie el juego.
        
        Args:
            callback (Callable[[Dict[str, Any]], None]): Función a llamar al iniciar el juego.
        """
        self.on_game_start = callback
    
    def set_game_update_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Establecer callback para actualizaciones del juego.
        
        Args:
            callback (Callable[[Dict[str, Any]], None]): Función a llamar en actualizaciones.
        """
        self.on_game_update = callback
    
    def set_shot_result_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Establecer callback para resultados de disparos.
        
        Args:
            callback (Callable[[Dict[str, Any]], None]): Función a llamar con resultados.
        """
        self.on_shot_result = callback
    
    def set_game_over_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Establecer callback para fin del juego.
        
        Args:
            callback (Callable[[Dict[str, Any]], None]): Función a llamar al terminar el juego.
        """
        self.on_game_over = callback
    
    def set_server_disconnect_callback(self, callback: Callable[[], None]) -> None:
        """Establecer callback para cuando se desconecte el servidor.
        
        Args:
            callback (Callable[[], None]): Función a llamar al desconectarse el servidor.
        """
        self.on_server_disconnect = callback