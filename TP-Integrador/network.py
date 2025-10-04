import socket
import json
import threading

class NetworkManager:
    def __init__(self):
        self.socket = None
        self.connected = False
        self.server_host = "localhost"
        self.server_port = 8888  # Puerto original
        self.player_id = None
        
        # Callbacks para eventos del servidor
        self.on_players_ready = None
        self.on_game_start = None
        self.on_game_update = None
        self.on_shot_result = None
        self.on_game_over = None
        
    def connect_to_server(self, host=None, port=None):
        """Intentar conectar al servidor"""
        if host:
            self.server_host = host
        if port:
            self.server_port = port
            
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            self.connected = True
            
            # Iniciar hilo para recibir mensajes
            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            
            return True
        except Exception as e:
            print(f"Error conectando al servidor: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Desconectar del servidor"""
        if self.socket:
            self.connected = False
            self.socket.close()
            self.socket = None
    
    def send_message(self, message_type, data=None):
        """Enviar mensaje al servidor"""
        if not self.connected:
            print("❌ No conectado al servidor")
            return False
            
        try:
            message = {
                'type': message_type,
                'player_id': self.player_id,
                'data': data
            }
            message_json = json.dumps(message) + '\n'  # Agregar salto de línea
            print(f"📤 Enviando mensaje al servidor: {message_json.strip()}")
            self.socket.send(message_json.encode('utf-8'))
            print(f"✅ Mensaje enviado exitosamente")
            return True
        except Exception as e:
            print(f"❌ Error enviando mensaje: {e}")
            return False
    
    def receive_messages(self):
        """Hilo para recibir mensajes del servidor"""
        buffer = ""
        while self.connected:
            try:
                data = self.socket.recv(1024).decode('utf-8')
                if data:
                    buffer += data
                    # Procesar mensajes separados por líneas
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        if line.strip():
                            try:
                                message = json.loads(line.strip())
                                self.handle_server_message(message)
                            except json.JSONDecodeError as e:
                                print(f"Error decodificando JSON: {e}")
                else:
                    break
            except Exception as e:
                print(f"Error recibiendo mensaje: {e}")
                break
        
        self.connected = False
    
    def handle_server_message(self, message):
        """Manejar mensajes recibidos del servidor"""
        message_type = message.get('type')
        data = message.get('data', {})
        
        if message_type == 'player_connect':
            self.player_id = data.get('player_id')
            print(f"ID de jugador asignado: {self.player_id}")
        
        elif message_type == 'players_ready':
            # Notificar sobre el estado de los jugadores
            if self.on_players_ready:
                self.on_players_ready(data)
        
        elif message_type == 'game_start':
            print(f"🎮 Mensaje GAME_START recibido del servidor: {data}")
            if self.on_game_start:
                print("📞 Llamando callback on_game_start")
                self.on_game_start(data)
            else:
                print("⚠️ No hay callback configurado para game_start")
        
        elif message_type == 'game_update':
            if self.on_game_update:
                self.on_game_update(data)
        
        elif message_type == 'shot_result':
            if self.on_shot_result:
                self.on_shot_result(data)
        
        elif message_type == 'game_over':
            if self.on_game_over:
                self.on_game_over(data)
        
        elif message_type == 'error':
            error_msg = data.get('error', 'Error desconocido')
            print(f"Error del servidor: {error_msg}")
    
    def place_ships(self, ship_positions):
        """Enviar posiciones de los barcos al servidor"""
        return self.send_message('place_ships', {'ships': ship_positions})
    
    def make_shot(self, x, y):
        """Enviar un disparo al servidor"""
        return self.send_message('shot', {'x': x, 'y': y})
    
    def start_game(self):
        """Solicitar inicio del juego"""
        print("🚀 INICIANDO: Enviando solicitud de inicio de juego al servidor")
        print(f"🔌 Estado de conexión: {self.connected}")
        print(f"🆔 ID del jugador: {self.player_id}")
        
        if not self.connected:
            print("❌ ERROR: No hay conexión al servidor")
            return False
            
        result = self.send_message('start_game', {})
        print(f"📤 Resultado del envío de start_game: {result}")
        return result
    
    def set_players_ready_callback(self, callback):
        """Establecer callback para cuando cambie el estado de jugadores"""
        self.on_players_ready = callback
    
    def set_game_start_callback(self, callback):
        """Establecer callback para cuando inicie el juego"""
        self.on_game_start = callback
    
    def set_game_update_callback(self, callback):
        """Establecer callback para actualizaciones del juego"""
        self.on_game_update = callback
    
    def set_shot_result_callback(self, callback):
        """Establecer callback para resultados de disparos"""
        self.on_shot_result = callback
    
    def set_game_over_callback(self, callback):
        """Establecer callback para fin del juego"""
        self.on_game_over = callback