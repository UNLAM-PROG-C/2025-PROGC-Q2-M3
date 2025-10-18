import pygame
import sys
import os
from menu import MenuScreen
from game import GameScreen
from network import NetworkManager

class GameOverScreen:
    def __init__(self, screen, is_winner=False):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.is_winner = is_winner
        
        # Configurar botón
        button_width = 200
        button_height = 60
        self.accept_button = {
            'rect': pygame.Rect(self.width // 2 - button_width // 2, self.height // 2 + 100, button_width, button_height),
            'text': 'ACEPTAR',
            'color': (70, 130, 180),
            'hover_color': (100, 149, 237),
            'text_color': (255, 255, 255)
        }
        
        self.font_large = pygame.font.Font(None, 96)
        self.font_medium = pygame.font.Font(None, 48)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Click izquierdo
                mouse_pos = pygame.mouse.get_pos()
                if self.accept_button['rect'].collidepoint(mouse_pos):
                    return "accept"
        return None
    
    def draw(self):
        # Fondo semi-transparente
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Texto principal
        if self.is_winner:
            main_text = "GANASTE"
            text_color = (0, 255, 0)  # Verde
        else:
            main_text = "PERDISTE"
            text_color = (255, 0, 0)  # Rojo
        
        # Dibujar texto principal
        text_surface = self.font_large.render(main_text, True, text_color)
        text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2 - 50))
        
        # Sombra del texto
        shadow_surface = self.font_large.render(main_text, True, (0, 0, 0))
        shadow_rect = shadow_surface.get_rect(center=(self.width // 2 + 3, self.height // 2 - 47))
        self.screen.blit(shadow_surface, shadow_rect)
        self.screen.blit(text_surface, text_rect)
        
        # Dibujar botón
        mouse_pos = pygame.mouse.get_pos()
        button_color = self.accept_button['hover_color'] if self.accept_button['rect'].collidepoint(mouse_pos) else self.accept_button['color']
        
        pygame.draw.rect(self.screen, button_color, self.accept_button['rect'])
        pygame.draw.rect(self.screen, (255, 255, 255), self.accept_button['rect'], 3)
        
        # Texto del botón
        button_text = self.font_medium.render(self.accept_button['text'], True, self.accept_button['text_color'])
        button_text_rect = button_text.get_rect(center=self.accept_button['rect'].center)
        self.screen.blit(button_text, button_text_rect)

class BattleshipClient:
    def __init__(self):
        pygame.init()
        
        # Definir tamaño mínimo de ventana para que los barcos se vean correctamente
        self.min_width = 1200
        self.min_height = 800
        
        # Definir tamaño inicial de ventana (no pantalla completa)
        initial_width = self.min_width
        initial_height = self.min_height
        
        # Establecer el título antes de crear la ventana
        pygame.display.set_caption("Batalla Naval - Cliente")
        
        # Crear ventana redimensionable con todos los controles (minimizar, restaurar/maximizar, cerrar)
        self.screen = pygame.display.set_mode((initial_width, initial_height), pygame.RESIZABLE)
        
        # Forzar la actualización de la ventana para asegurar que la barra de título aparezca
        pygame.display.flip()
        self.width = self.screen.get_width()
        self.height = self.screen.get_height()
        self.clock = pygame.time.Clock()
        
        # Estados del juego
        self.current_state = "menu"
        self.running = True
        
        # Inicializar network manager primero
        self.network_manager = NetworkManager()
        
        # Inicializar pantallas
        self.menu_screen = MenuScreen(self.screen)
        self.game_screen = GameScreen(self.screen, self.network_manager)
        self.game_over_screen = None  # Se creará cuando sea necesario
        
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
                    
                    # Recrear game over screen si existe
                    if self.game_over_screen is not None:
                        is_winner = self.game_over_screen.is_winner
                        self.game_over_screen = GameOverScreen(self.screen, is_winner)
                    
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
                elif self.current_state == "game_over":
                    action = self.game_over_screen.handle_event(event)
                    if action == "accept":
                        # Desconectar del servidor al terminar el juego
                        if self.network_manager.connected:
                            self.network_manager.disconnect()
                            print("Desconectado del servidor después del juego")
                        
                        # Resetear estado del menú para mostrar desconectado
                        self.menu_screen.set_connection_status(False, False)
                        
                        # Volver al menú
                        self.current_state = "menu"
                        self.game_over_screen = None
            
            # Renderizar según el estado actual
            if self.current_state == "menu":
                self.menu_screen.update()
                self.menu_screen.draw()
            elif self.current_state == "game":
                self.game_screen.update()
                self.game_screen.draw()
            elif self.current_state == "game_over":
                # Dibujar el juego de fondo y encima la pantalla de game over
                self.game_screen.update()
                self.game_screen.draw()
                self.game_over_screen.draw()
            
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
        
        # Obtener si el jugador ganó o perdió
        is_winner = data.get('is_winner', False)
        
        # Crear pantalla de game over
        self.game_over_screen = GameOverScreen(self.screen, is_winner)
        
        # Cambiar al estado de game over
        self.current_state = "game_over"

if __name__ == "__main__":
    client = BattleshipClient()
    client.run()