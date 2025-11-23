import socket
import json
import threading
import sys
import os
from typing import Optional, Callable, Any, Dict

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from constants import (DEFAULT_SERVER_HOST, DEFAULT_SERVER_PORT, NETWORK_BUFFER_SIZE, 
                      THREAD_DAEMON_MODE, NETWORK_ENCODING, MESSAGE_BUFFER_SPLIT_LIMIT,
                      MESSAGE_TYPES, NETWORK_LOG_MESSAGES, JSON_MESSAGE_DELIMITER)

class NetworkManager:
    def __init__(self):
        self._initialize_connection_attributes()
        self._initialize_server_config()
        self._initialize_callbacks()
        
    def _initialize_connection_attributes(self) -> None:
        self.socket: Optional[socket.socket] = None
        self.connected: bool = False
        self.player_id: Optional[str] = None
        
    def _initialize_server_config(self) -> None:
        self.server_host: str = DEFAULT_SERVER_HOST
        self.server_port: int = DEFAULT_SERVER_PORT
        
    def _initialize_callbacks(self) -> None:
        self.on_players_ready: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_game_start: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_game_update: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_shot_result: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_game_over: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_server_disconnect: Optional[Callable[[], None]] = None
    
    def connect_to_server(self, host: Optional[str] = None, port: Optional[int] = None) -> bool:
        self._update_server_config(host, port)
        
        try:
            return self._establish_connection()
        except Exception as e:
            print(f"Error conectando al servidor: {e}")
            self.connected = False
            return False
            
    def _update_server_config(self, host: Optional[str], port: Optional[int]) -> None:
        if host:
            self.server_host = host
        if port:
            self.server_port = port
            
    def _establish_connection(self) -> bool:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.server_host, self.server_port))
        self.connected = True
        
        self._start_receive_thread()
        return True
        
    def _start_receive_thread(self) -> None:
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.daemon = THREAD_DAEMON_MODE
        self.receive_thread.start()

    def disconnect(self) -> None:
        if self.socket:
            self.connected = False
            self.socket.close()
            self.socket = None
            
    def send_message(self, message_type: str, data: Optional[Dict[str, Any]] = None) -> bool:
        if not self.connected:
            print(NETWORK_LOG_MESSAGES['NOT_CONNECTED'])
            return False
            
        try:
            message = self._create_message(message_type, data)
            return self._send_raw_message(message)
        except (ConnectionResetError, ConnectionAbortedError):
            return self._handle_connection_error()
        except Exception as e:
            print(f"Error enviando mensaje: {e}")
            return False
            
    def _create_message(self, message_type: str, data: Optional[Dict[str, Any]]) -> str:
        message = {
            'type': message_type,
            'player_id': self.player_id,
            'data': data
        }
        return json.dumps(message) + JSON_MESSAGE_DELIMITER
        
    def _send_raw_message(self, message_json: str) -> bool:
        print(f"Enviando mensaje al servidor: {message_json.strip()}")
        self.socket.send(message_json.encode(NETWORK_ENCODING))
        print(NETWORK_LOG_MESSAGES['SEND_SUCCESS'])
        return True
        
    def _handle_connection_error(self) -> bool:
        print(NETWORK_LOG_MESSAGES['SERVER_DISCONNECTED'])
        self.connected = False
        if self.on_server_disconnect:
            self.on_server_disconnect()
        return False
    
    def receive_messages(self) -> None:
        buffer: str = ""
        
        while self.connected:
            buffer = self._process_incoming_data(buffer)
            
    def _process_incoming_data(self, buffer: str) -> str:
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
        print(NETWORK_LOG_MESSAGES['NO_DATA_RECEIVED'])
        self.connected = False
        if self.on_server_disconnect:
            print(NETWORK_LOG_MESSAGES['NOTIFYING_DISCONNECT'])
            self.on_server_disconnect()
            
    def _handle_server_disconnection_error(self) -> None:
        print(NETWORK_LOG_MESSAGES['CONNECTION_RESET'])
        self.connected = False
        if self.on_server_disconnect:
            self.on_server_disconnect()
            
    def _process_message_buffer(self, buffer: str) -> str:
        while JSON_MESSAGE_DELIMITER in buffer:
            message, buffer = buffer.split(JSON_MESSAGE_DELIMITER, MESSAGE_BUFFER_SPLIT_LIMIT)
            if message.strip():
                self._handle_complete_message(message)
        return buffer
        
    def _handle_complete_message(self, message: str) -> None:
        print(f"Mensaje recibido del servidor: {message}")
        try:
            parsed_message = json.loads(message)
            self.handle_server_message(parsed_message)
        except json.JSONDecodeError as e:
            print(f"{NETWORK_LOG_MESSAGES['PARSING_ERROR']}: {e}")
            
    def _handle_receive_error(self, error: Exception) -> None:
        print(f"Error recibiendo mensaje: {error}")
        
        self.connected = False
        if self.on_server_disconnect:
            self.on_server_disconnect()
    
    def handle_server_message(self, message: Dict[str, Any]) -> None:
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
        self.player_id = data.get('player_id')
        print(f"ID de jugador asignado: {self.player_id}")
        
    def _handle_players_ready(self, data: Dict[str, Any]) -> None:
        if self.on_players_ready:
            self.on_players_ready(data)
            
    def _handle_game_start(self, data: Dict[str, Any]) -> None:
        print(f"Mensaje GAME_START recibido del servidor: {data}")
        if self.on_game_start:
            print("Llamando callback on_game_start")
            self.on_game_start(data)
        else:
            print(NETWORK_LOG_MESSAGES['NO_GAME_START_CALLBACK'])
            
    def _handle_game_update(self, data: Dict[str, Any]) -> None:
        if self.on_game_update:
            self.on_game_update(data)
            
    def _handle_shot_result(self, data: Dict[str, Any]) -> None:
        if self.on_shot_result:
            self.on_shot_result(data)
            
    def _handle_game_over(self, data: Dict[str, Any]) -> None:
        if self.on_game_over:
            self.on_game_over(data)
            
    def _handle_player_disconnect(self, data: Dict[str, Any]) -> None:
        print(f"MENSAJE PLAYER_DISCONNECT RECIBIDO: {data}")
        disconnected_player = data.get('disconnected_player', NETWORK_LOG_MESSAGES['UNKNOWN_PLAYER'])
        message = data.get('message', NETWORK_LOG_MESSAGES['DEFAULT_DISCONNECT_MESSAGE'])
        print(f"{message} (Jugador: {disconnected_player})")
        
        if self.on_server_disconnect:
            print("Llamando callback de desconexión por jugador desconectado")
            self.on_server_disconnect()
        else:
            print(NETWORK_LOG_MESSAGES['NO_PLAYER_DISCONNECT_CALLBACK'])
            
    def _handle_error(self, data: Dict[str, Any]) -> None:
        error_msg = data.get('error', NETWORK_LOG_MESSAGES['DEFAULT_ERROR_MESSAGE'])
        print(f"Error del servidor: {error_msg}")
    
    def place_ships(self, ship_positions: Dict[str, Any]) -> bool:
        return self.send_message(MESSAGE_TYPES['PLACE_SHIPS'], {'ships': ship_positions})
    
    def make_shot(self, x: int, y: int) -> bool:
        return self.send_message(MESSAGE_TYPES['SHOT'], {'x': x, 'y': y})
    
    def start_game(self) -> bool:
        self._log_start_game_info()
        
        if not self._validate_connection():
            return False
            
        result = self.send_message(MESSAGE_TYPES['START_GAME'], {})
        print(f"Resultado del envío de start_game: {result}")
        return result
        
    def _log_start_game_info(self) -> None:
        print("INICIANDO: Enviando solicitud de inicio de juego al servidor")
        print(f"Estado de conexión: {self.connected}")
        print(f"ID del jugador: {self.player_id}")
        
    def _validate_connection(self) -> bool:
        if not self.connected:
            print(NETWORK_LOG_MESSAGES['NO_CONNECTION'])
            return False
        return True
    
    def set_players_ready_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        self.on_players_ready = callback
    
    def set_game_start_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        self.on_game_start = callback
    
    def set_game_update_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        self.on_game_update = callback
    
    def set_shot_result_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        self.on_shot_result = callback
    
    def set_game_over_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        self.on_game_over = callback
    
    def set_server_disconnect_callback(self, callback: Callable[[], None]) -> None:
        self.on_server_disconnect = callback