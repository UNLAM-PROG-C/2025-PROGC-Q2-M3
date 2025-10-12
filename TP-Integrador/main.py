import pygame
import sys
import os
from menu import MenuScreen
from game import GameScreen
from network import NetworkManager

class BattleshipClient:
    def __init__(self):
        pygame.init()
        
        # Definir tamaño mínimo de ventana para que los barcos se vean correctamente
        self.min_width = 1200
        self.min_height = 800
        
        # Obtener el tamaño de la pantalla
        info = pygame.display.Info()
        screen_width = info.current_w
        screen_height = info.current_h - 40  # Restar espacio para la barra de tareas
        
        # Asegurar que el tamaño inicial respete el mínimo
        initial_width = max(screen_width, self.min_width)
        initial_height = max(screen_height, self.min_height)
        
        # Crear ventana redimensionable con todos los controles (minimizar, restaurar/maximizar, cerrar)
        self.screen = pygame.display.set_mode((initial_width, initial_height), pygame.RESIZABLE)
        self.width = self.screen.get_width()
        self.height = self.screen.get_height()
        pygame.display.set_caption("Batalla Naval - Cliente")
        self.clock = pygame.time.Clock()
        
        # Estados del juego
        self.current_state = "menu"
        self.running = True
        
        # Inicializar network manager primero
        self.network_manager = NetworkManager()
        
        # Inicializar pantallas
        self.menu_screen = MenuScreen(self.screen)
        self.game_screen = GameScreen(self.screen, self.network_manager)
        
        # Configurar callbacks de red
        self.setup_network_callbacks()
        
    def run(self):
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    # Aplicar tamaño mínimo para evitar que los barcos se vean mal
                    new_width = max(event.w, self.min_width)
                    new_height = max(event.h, self.min_height)
                    
                    # Actualizar dimensiones cuando se redimensiona la ventana
                    self.width = new_width
                    self.height = new_height
                    self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                    
                    # Preservar el estado del juego antes de recrear las pantallas
                    if hasattr(self, 'game_screen') and self.current_state == "game":
                        # Guardar el estado actual del juego
                        saved_game_state = {
                            'game_phase': self.game_screen.game_phase,
                            'current_ship_index': self.game_screen.current_ship_index,
                            'ship_horizontal': self.game_screen.ship_horizontal,
                            'my_turn': self.game_screen.my_turn,
                            'my_ships': self.game_screen.my_board.ships.copy() if hasattr(self.game_screen, 'my_board') else [],
                            'enemy_shots': self.game_screen.enemy_board.shots.copy() if hasattr(self.game_screen, 'enemy_board') else {}
                        }
                        
                        # Recrear la pantalla de juego con las nuevas dimensiones
                        self.game_screen = GameScreen(self.screen, self.network_manager)
                        
                        # Restaurar el estado del juego
                        self.game_screen.game_phase = saved_game_state['game_phase']
                        self.game_screen.current_ship_index = saved_game_state['current_ship_index']
                        self.game_screen.ship_horizontal = saved_game_state['ship_horizontal']
                        self.game_screen.my_turn = saved_game_state['my_turn']
                        
                        # Restaurar los barcos colocados
                        self.game_screen.my_board.ships = saved_game_state['my_ships']
                        
                        # Restaurar los disparos del enemigo
                        self.game_screen.enemy_board.shots = saved_game_state['enemy_shots']
                    else:
                        # Si no estamos en el juego, recrear normalmente
                        self.game_screen = GameScreen(self.screen, self.network_manager)
                    
                    # Actualizar el menú
                    self.menu_screen = MenuScreen(self.screen)
                    self.setup_network_callbacks()
                    
                # Manejar eventos según el estado actual
                if self.current_state == "menu":
                    action = self.menu_screen.handle_event(event)
                    if action == "connect":
                        # Intentar conectar al servidor - mantenerse en menú
                        if self.network_manager.connect_to_server():
                            print("Conectado al servidor exitosamente")
                        else:
                            print("Error: No se pudo conectar al servidor")
                    elif action == "start_game":
                        # Solicitar inicio del juego al servidor
                        if self.network_manager.start_game():
                            print("Solicitando inicio de partida...")
                        
                elif self.current_state == "game":
                    self.game_screen.handle_event(event)
            
            # Renderizar según el estado actual
            if self.current_state == "menu":
                self.menu_screen.update()
                self.menu_screen.draw()
            elif self.current_state == "game":
                self.game_screen.update()
                self.game_screen.draw()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()
    
    def setup_network_callbacks(self):
        """Configurar callbacks para eventos de red"""
        self.network_manager.set_players_ready_callback(self.on_players_ready)
        self.network_manager.set_game_start_callback(self.on_game_start)
        self.network_manager.set_game_update_callback(self.on_game_update)
        self.network_manager.set_shot_result_callback(self.on_shot_result)
        self.network_manager.set_game_over_callback(self.on_game_over)
    
    def on_players_ready(self, data):
        """Callback cuando cambia el estado de jugadores conectados"""
        connected = data.get('connected_players', 0) > 0
        players_ready = data.get('players_ready', False)
        self.menu_screen.set_connection_status(connected, players_ready)
    
    def on_game_start(self, data):
        """Callback cuando inicia el juego"""
        print(f"🎮 MENSAJE GAME_START RECIBIDO: {data}")
        print("✅ El servidor confirmó el inicio del juego")
        print("🚀 Redirigiendo AMBOS clientes a la pantalla de juego...")
        
        # Cambiar automáticamente a la pantalla de juego (pantalla en blanco inicialmente)
        self.current_state = "game"
        print("✅ Estado cambiado a 'game' - Pantalla de juego activa")
    
    def on_game_update(self, data):
        """Callback para actualizaciones del juego"""
        # Actualizar estado del juego según los datos del servidor
        phase = data.get('phase')
        current_turn = data.get('current_turn')
        
        if phase == 'battle_phase':
            self.game_screen.start_battle_phase()
            # Verificar si es mi turno
            is_my_turn = current_turn == self.network_manager.player_id
            self.game_screen.set_my_turn(is_my_turn)
    
    def on_shot_result(self, data):
        """Callback para resultados de disparos"""
        # Actualizar tableros con resultado del disparo
        if hasattr(self.game_screen, 'handle_shot_result'):
            self.game_screen.handle_shot_result(data)
    
    def on_game_over(self, data):
        """Callback cuando termina el juego"""
        print(f"Juego terminado: {data}")
        # Volver al menú después del juego
        self.current_state = "menu"

if __name__ == "__main__":
    client = BattleshipClient()
    client.run()