"""Main client for Battleship Naval game
Handles main window, game states and graphical interface"""

import pygame
import sys
import os

# Importar constants y las clases del paquete
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from constants import *

# Constantes específicas del cliente principal
INFINITE_LOOP = -1
VIDEO_RESIZE_VALIDATION_DELAY = 0
CONNECTION_CHECK_INTERVAL = 1
MUTED_VOLUME = 0.0
AUDIO_FILE_EXTENSION = '.mp3'
PIRATE_MUSIC_FILE = 'piratas.mp3'
BACKGROUND_MUSIC_FILE = 'background.mp3'

# Importar las clases desde este paquete
from .menu_screen import MenuScreen
from .game_screen import GameScreen
from .network_manager import NetworkManager
from .connection_dialog import ConnectionDialog
from .game_over_screen import GameOverScreen

class BattleshipClient:
    def __init__(self):
        self._initialize_pygame_systems()
        self._setup_window_configuration()
        self._initialize_game_state()
        self._initialize_screens_and_managers()
        self._setup_audio_system()
    
    def _initialize_pygame_systems(self):
        """Inicializar sistemas básicos de pygame"""
        pygame.init()
        self._initialize_audio_mixer()
    
    def _initialize_audio_mixer(self):
        """Configurar mixer de audio con parámetros optimizados"""
        pygame.mixer.pre_init(
            frequency=MIXER_FREQUENCY, 
            size=MIXER_SIZE, 
            channels=MIXER_CHANNELS, 
            buffer=MIXER_BUFFER
        )
        pygame.mixer.init()
    
    def _setup_window_configuration(self):
        """Configurar tamaños y propiedades de ventana"""
        self.min_width = MIN_WINDOW_WIDTH
        self.min_height = MIN_WINDOW_HEIGHT
        self._create_game_window()
    
    def _create_game_window(self):
        """Crear ventana principal del juego"""
        pygame.display.set_caption("Batalla Naval - Cliente")
        self.screen = pygame.display.set_mode(
            (INITIAL_WINDOW_WIDTH, INITIAL_WINDOW_HEIGHT), 
            pygame.RESIZABLE
        )
        self._finalize_window_setup()
    
    def _finalize_window_setup(self):
        """Finalizar configuración de ventana y clock"""
        pygame.display.flip()
        self.width = self.screen.get_width()
        self.height = self.screen.get_height()
        self.clock = pygame.time.Clock()
    
    def _initialize_game_state(self):
        """Inicializar variables de estado del juego"""
        self.current_state = "menu"
        self.running = True
    
    def _initialize_screens_and_managers(self):
        """Inicializar pantallas y administradores de red"""
        self.network_manager = NetworkManager()
        self.menu_screen = MenuScreen(self.screen)
        self.game_screen = GameScreen(self.screen, self.network_manager)
        self.game_over_screen = None
        self.setup_network_callbacks()
    
    def _setup_audio_system(self):
        """Configurar sistema de audio y música de fondo"""
        self.init_background_music()
    
    def init_background_music(self):
        """Inicializar y reproducir música de fondo"""
        try:
            self._load_and_play_menu_music()
            self._display_music_success_message()
        except pygame.error as e:
            self._handle_music_pygame_error(e)
        except FileNotFoundError:
            self._handle_music_file_not_found()
    
    def _load_and_play_menu_music(self):
        """Cargar y reproducir música del menú"""
        music_path = self._get_menu_music_path()
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(MUSIC_VOLUME_MENU)
        pygame.mixer.music.play(INFINITE_LOOP)
    
    def _get_menu_music_path(self):
        """Obtener ruta del archivo de música del menú"""
        return os.path.join("assets", "sounds", PIRATE_MUSIC_FILE)
    
    def _display_music_success_message(self):
        """Mostrar mensaje de éxito al cargar música"""
        print(f"✅ Música de fondo '{PIRATE_MUSIC_FILE}' iniciada")
    
    def _handle_music_pygame_error(self, error):
        """Manejar errores de pygame al cargar música"""
        print(f"❌ Error al cargar música de fondo: {error}")
    
    def _handle_music_file_not_found(self):
        """Manejar error de archivo de música no encontrado"""
        print(f"❌ No se encontró el archivo {PIRATE_MUSIC_FILE}")

    def run(self):
        """Bucle principal del juego"""
        while self.running:
            self._process_game_events()
            self._check_connection_status()
            self._render_current_state()
            self._update_display_and_clock()
        self._cleanup_and_exit()
    
    def _process_game_events(self):
        """Procesar todos los eventos del juego"""
        events = pygame.event.get()
        for event in events:
            self._handle_system_events(event)
            self._handle_state_specific_events(event)
    
    def _handle_system_events(self, event):
        """Manejar eventos del sistema (quit, escape, resize)"""
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            self.running = False
        elif event.type == pygame.VIDEORESIZE:
            self._handle_window_resize(event)
    
    def _handle_window_resize(self, event):
        """Manejar redimensionamiento de ventana"""
        self._update_window_dimensions(event)
        self._preserve_and_recreate_screens()
    
    def _update_window_dimensions(self, event):
        """Actualizar dimensiones de ventana con validación de tamaño mínimo"""
        self.width = max(event.w, self.min_width)
        self.height = max(event.h, self.min_height)
        self.screen = pygame.display.set_mode(
            (self.width, self.height), pygame.RESIZABLE
        )
    
    def _preserve_and_recreate_screens(self):
        """Preservar estado del juego y recrear pantallas"""
        if self._should_preserve_game_state():
            self._preserve_and_restore_game_state()
        else:
            self._recreate_game_screen()
        self._recreate_other_screens()
    
    def _should_preserve_game_state(self):
        """Verificar si se debe preservar el estado del juego"""
        return (hasattr(self, 'game_screen') and 
                self.current_state == "game")
    
    def _preserve_and_restore_game_state(self):
        """Preservar y restaurar estado del juego durante resize"""
        saved_state = self._save_current_game_state()
        self._recreate_game_screen()
        self._restore_game_state(saved_state)
    
    def _save_current_game_state(self):
        """Guardar estado actual del juego"""
        return {
            'game_phase': self.game_screen.game_phase,
            'current_ship_index': self.game_screen.current_ship_index,
            'ship_horizontal': self.game_screen.ship_horizontal,
            'my_turn': self.game_screen.my_turn,
            'my_ships': self._get_my_ships_copy(),
            'enemy_shots': self._get_enemy_shots_copy()
        }
    
    def _get_my_ships_copy(self):
        """Obtener copia de los barcos propios"""
        if hasattr(self.game_screen, 'my_board'):
            return self.game_screen.my_board.ships.copy()
        return []
    
    def _get_enemy_shots_copy(self):
        """Obtener copia de los disparos del enemigo"""
        if hasattr(self.game_screen, 'enemy_board'):
            return self.game_screen.enemy_board.shots.copy()
        return {}
    
    def _recreate_game_screen(self):
        """Recrear pantalla de juego"""
        self.game_screen = GameScreen(self.screen, self.network_manager)
    
    def _restore_game_state(self, saved_state):
        """Restaurar estado del juego desde datos guardados"""
        self.game_screen.game_phase = saved_state['game_phase']
        self.game_screen.current_ship_index = saved_state['current_ship_index']
        self.game_screen.ship_horizontal = saved_state['ship_horizontal']
        self.game_screen.my_turn = saved_state['my_turn']
        self.game_screen.my_board.ships = saved_state['my_ships']
        self.game_screen.enemy_board.shots = saved_state['enemy_shots']
    
    def _recreate_other_screens(self):
        """Recrear menú y pantalla de game over si existe"""
        self.menu_screen = MenuScreen(self.screen)
        self.setup_network_callbacks()
        self._recreate_game_over_screen_if_needed()
    
    def _recreate_game_over_screen_if_needed(self):
        """Recrear pantalla de game over si existe"""
        if self.game_over_screen is not None:
            is_winner = self.game_over_screen.is_winner
            self.game_over_screen = GameOverScreen(self.screen, is_winner)
        
    def _handle_state_specific_events(self, event):
        """Manejar eventos específicos según el estado actual"""
        if self.current_state == "menu":
            self._handle_menu_events(event)
        elif self.current_state == "game":
            self._handle_game_events(event)
        elif self.current_state == "game_over":
            self._handle_game_over_events(event)
    
    def _handle_menu_events(self, event):
        """Manejar eventos del menú"""
        action = self.menu_screen.handle_event(event)
        self._process_menu_action(action)
    
    def _process_menu_action(self, action):
        """Procesar acción del menú"""
        if action == "connect":
            self._handle_connect_action()
        elif action == "start_game":
            self._handle_start_game_action()
        elif action == "toggle_music":
            self._handle_toggle_music_action()
    
    def _handle_connect_action(self):
        """Manejar acción de conexión"""
        connection_dialog = ConnectionDialog(self.screen)
        connection_config = connection_dialog.run()
        
        if connection_config:
            self._attempt_server_connection(connection_config)
        else:
            self._display_connection_cancelled_message()
    
    def _attempt_server_connection(self, config):
        """Intentar conexión al servidor con configuración dada"""
        host, port = config['host'], config['port']
        self._display_connection_attempt_info(host, port)
        
        if self.network_manager.connect_to_server(host, port):
            self._display_connection_success(host, port)
        else:
            self._display_connection_failure(host, port)
    
    def _display_connection_attempt_info(self, host, port):
        """Mostrar información del intento de conexión"""
        print(f"🔌 Intentando conectar al servidor...")
        print(f"   Host: {host}")
        print(f"   Puerto: {port}")
    
    def _display_connection_success(self, host, port):
        """Mostrar mensaje de conexión exitosa"""
        print(f"✅ Conectado exitosamente a {host}:{port}")
    
    def _display_connection_failure(self, host, port):
        """Mostrar mensaje de error de conexión"""
        print(f"❌ Error: No se pudo conectar a {host}:{port}")
    
    def _display_connection_cancelled_message(self):
        """Mostrar mensaje de conexión cancelada"""
        print("❌ Conexión cancelada por el usuario")
    
    def _handle_start_game_action(self):
        """Manejar acción de inicio de juego"""
        if self.network_manager.start_game():
            print("Solicitando inicio de partida...")
    
    def _handle_toggle_music_action(self):
        """Manejar acción de alternar música"""
        self.menu_screen.toggle_music_mute()
    
    def _handle_game_events(self, event):
        """Manejar eventos durante el juego"""
        self.game_screen.handle_event(event)
    
    def _handle_game_over_events(self, event):
        """Manejar eventos en pantalla de game over"""
        action = self.game_over_screen.handle_event(event)
        if action == "accept" or self.game_over_screen.auto_return:
            self._handle_game_over_accept()
    
    def _handle_game_over_accept(self):
        """Manejar aceptación en pantalla de game over"""
        self._disconnect_after_game()
        self._reset_menu_state()
        self._restart_menu_music()
        self._return_to_menu()
    
    def _disconnect_after_game(self):
        """Desconectar del servidor después del juego"""
        if self.network_manager.connected:
            self.network_manager.disconnect()
            print("Desconectado del servidor después del juego")
    
    def _reset_menu_state(self):
        """Resetear estado del menú"""
        self.menu_screen.set_connection_status(False, False)
    
    def _restart_menu_music(self):
        """Reiniciar música del menú"""
        self.init_background_music()
        self._apply_mute_if_needed()
    
    def _apply_mute_if_needed(self):
        """Aplicar silencio si está activado en el menú"""
        if hasattr(self.menu_screen, 'music_muted') and self.menu_screen.music_muted:
            pygame.mixer.music.set_volume(MUTED_VOLUME)
    
    def _return_to_menu(self):
        """Volver al menú principal"""
        self.current_state = "menu"
        self.game_over_screen = None
    
    def _check_connection_status(self):
        """Verificar estado de conexión periódicamente"""
        if self._should_check_connection():
            if not self.network_manager.connected:
                print("🔌 Detección de desconexión en bucle principal")
                self.on_server_disconnect()
    
    def _should_check_connection(self):
        """Verificar si se debe chequear el estado de conexión"""
        return (self.current_state != "menu" and 
                hasattr(self.network_manager, 'connected') and
                self.current_state in ["game", "game_over"])
    
    def _render_current_state(self):
        """Renderizar según el estado actual"""
        if self.current_state == "menu":
            self._render_menu_state()
        elif self.current_state == "game":
            self._render_game_state()
        elif self.current_state == "game_over":
            self._render_game_over_state()
    
    def _render_menu_state(self):
        """Renderizar estado del menú"""
        self.menu_screen.update()
        self.menu_screen.draw()
    
    def _render_game_state(self):
        """Renderizar estado del juego"""
        self.game_screen.update()
        self.game_screen.draw()
    
    def _render_game_over_state(self):
        """Renderizar estado de game over"""
        self.game_screen.update()
        self.game_screen.draw()
        self.game_over_screen.draw()
    
    def _update_display_and_clock(self):
        """Actualizar pantalla y reloj del juego"""
        pygame.display.flip()
        self.clock.tick(TARGET_FPS)
    
    def _cleanup_and_exit(self):
        """Limpiar recursos y salir del juego"""
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        pygame.quit()
        sys.exit()
    
    def setup_network_callbacks(self):
        """Configurar callbacks para eventos de red"""
        self.network_manager.set_players_ready_callback(self.on_players_ready)
        self.network_manager.set_game_start_callback(self.on_game_start)
        self.network_manager.set_game_update_callback(self.on_game_update)
        self.network_manager.set_shot_result_callback(self.on_shot_result)
        self.network_manager.set_game_over_callback(self.on_game_over)
        self.network_manager.set_server_disconnect_callback(self.on_server_disconnect)
    
    def on_players_ready(self, data):
        """Callback cuando cambia el estado de jugadores conectados"""
        connected = data.get('connected_players', 0) > 0
        players_ready = data.get('players_ready', False)
        self.menu_screen.set_connection_status(connected, players_ready)
    
    def on_game_start(self, data):
        """Callback cuando inicia el juego"""
        self._display_game_start_messages(data)
        self._transition_audio_to_game()
        self._reset_game_state_for_new_game()
        self._change_to_game_state()
    
    def _display_game_start_messages(self, data):
        """Mostrar mensajes de inicio de juego"""
        print(f"🎮 MENSAJE GAME_START RECIBIDO: {data}")
        print("✅ El servidor confirmó el inicio del juego")
        print("🚀 Redirigiendo AMBOS clientes a la pantalla de juego...")
    
    def _transition_audio_to_game(self):
        """Transicionar audio del menú al juego"""
        self._stop_menu_music()
        self._start_game_music()
    
    def _stop_menu_music(self):
        """Detener música del menú"""
        pygame.mixer.music.stop()
        print("🔇 Música del menú detenida")
    
    def _start_game_music(self):
        """Iniciar música del juego"""
        try:
            self._load_and_play_game_music()
            self._display_game_music_success()
        except pygame.error as e:
            self._handle_game_music_pygame_error(e)
        except FileNotFoundError:
            self._handle_game_music_file_not_found()
    
    def _load_and_play_game_music(self):
        """Cargar y reproducir música del juego"""
        game_music_path = self._get_game_music_path()
        pygame.mixer.music.load(game_music_path)
        pygame.mixer.music.set_volume(MUSIC_VOLUME_GAME)
        pygame.mixer.music.play(INFINITE_LOOP)
    
    def _get_game_music_path(self):
        """Obtener ruta del archivo de música del juego"""
        return os.path.join("assets", "sounds", BACKGROUND_MUSIC_FILE)
    
    def _display_game_music_success(self):
        """Mostrar mensaje de éxito al cargar música del juego"""
        print(f"🎵 Música de fondo del juego '{BACKGROUND_MUSIC_FILE}' iniciada")
    
    def _handle_game_music_pygame_error(self, error):
        """Manejar errores de pygame al cargar música del juego"""
        print(f"❌ Error al cargar música de juego: {error}")
    
    def _handle_game_music_file_not_found(self):
        """Manejar error de archivo de música del juego no encontrado"""
        print(f"❌ No se encontró el archivo {BACKGROUND_MUSIC_FILE}")
    
    def _reset_game_state_for_new_game(self):
        """Resetear estado del juego para nueva partida"""
        self._reset_game_state_safely("Error reseteando pantalla de juego")
    
    def _reset_game_state_after_game_over(self):
        """Resetear estado del juego después de game over"""
        self._reset_game_state_safely("Error reseteando pantalla tras game over")
    
    def _reset_game_state_safely(self, error_msg):
        """Resetear estado del juego de forma segura con manejo de errores"""
        if hasattr(self, 'game_screen') and self.game_screen is not None:
            try:
                self.game_screen.reset_game_state()
            except Exception as e:
                print(f"⚠️ {error_msg}: {e}")
    
    def _change_to_game_state(self):
        """Cambiar al estado de juego"""
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
        self._stop_game_music()
        self._reset_game_state_after_game_over()
        self._create_and_show_game_over_screen(data)
    
    def _stop_game_music(self):
        """Detener música del juego"""
        pygame.mixer.music.stop()
        print("🔇 Música de juego detenida")
    
    def _create_and_show_game_over_screen(self, data):
        """Crear y mostrar pantalla de game over"""
        is_winner = data.get('is_winner', False)
        self.game_over_screen = GameOverScreen(self.screen, is_winner)
        self.current_state = "game_over"
    
    def on_server_disconnect(self):
        """Callback cuando se desconecta el servidor o un jugador"""
        self._display_disconnect_message()
        self._stop_all_music()
        self._reset_network_manager_state()
        self._reset_menu_and_restart_music()
        self._return_to_menu_after_disconnect()
    
    def _display_disconnect_message(self):
        """Mostrar mensaje de desconexión apropiado"""
        if self.current_state in ["game", "game_over"]:
            print("🔌 Oponente desconectado - Redirigiendo al menú principal")
        else:
            print("🔌 Servidor desconectado - Redirigiendo al menú principal")
    
    def _stop_all_music(self):
        """Detener toda música activa"""
        pygame.mixer.music.stop()
        print("🔇 Música detenida por desconexión")
    
    def _reset_network_manager_state(self):
        """Resetear estado del administrador de red"""
        self.network_manager.connected = False
        self.network_manager.player_id = None
    
    def _reset_menu_and_restart_music(self):
        """Resetear menú y reiniciar música"""
        self.menu_screen.set_connection_status(False, False)
        self.init_background_music()
        self._restore_music_mute_state()
    
    def _restore_music_mute_state(self):
        """Restaurar estado de silencio si estaba activado"""
        self._apply_mute_if_needed()
    
    def _return_to_menu_after_disconnect(self):
        """Volver al menú principal después de desconexión"""
        self.current_state = "menu"
        self.game_over_screen = None
        print("✅ Redirigido al menú principal")