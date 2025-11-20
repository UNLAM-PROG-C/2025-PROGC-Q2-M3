"""Módulo de la pantalla del menú principal del juego Batalla Naval.

Este módulo contiene la implementación de MenuScreen que maneja
la interfaz del menú principal, incluyendo conexión al servidor,
inicio de partidas y controles de música.
"""

import pygame
import os
import sys
from typing import Optional, Tuple, Dict, Any

# Importar constants desde la carpeta padre del proyecto
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from constants import (COLOR_WHITE, MENU_BUTTON_WIDTH, MENU_BUTTON_HEIGHT, MENU_BUTTON_Y_CONNECT,
                      MENU_BUTTON_Y_START, COLOR_BUTTON_CONNECT, COLOR_BUTTON_CONNECT_HOVER,
                      COLOR_BUTTON_START, COLOR_BUTTON_START_HOVER, COLOR_BUTTON_DISABLED,
                      MUTE_BUTTON_WIDTH, MUTE_BUTTON_HEIGHT, MUTE_BUTTON_MARGIN, COLOR_BUTTON_MUTE,
                      COLOR_BUTTON_MUTE_HOVER, FONT_SIZE_NORMAL, FONT_SIZE_SMALL, COLOR_BUTTON_CONNECT_ACTIVE,
                      COLOR_GREEN, COLOR_YELLOW, MENU_STATUS_Y, MUTED_VOLUME, MUSIC_VOLUME_MENU,
                      MENU_BUTTON_DIVISION_FACTOR, MENU_BUTTON_BORDER_WIDTH, MUTE_BUTTON_BORDER_WIDTH,
                      MENU_FONT_SIZE_DEFAULT, MOUSE_BUTTON_LEFT, MENU_STATE_DISCONNECTED,
                      MENU_STATE_CONNECTED, MENU_STATE_PLAYERS_NOT_READY, MENU_STATE_PLAYERS_READY,
                      MENU_TEXT, MENU_STATUS_COLOR_DISCONNECTED, MENU_BACKGROUND_COLOR_DEFAULT,
                      MENU_EVENTS)

class MenuScreen:
    """Pantalla del menú principal del juego Batalla Naval.
    
    Esta clase maneja la interfaz del menú principal, incluyendo la visualización
    de botones, manejo de eventos, conexión al servidor y controles de música.
    
    Attributes:
        screen (pygame.Surface): Superficie de pantalla principal.
        width (int): Ancho de la pantalla.
        height (int): Alto de la pantalla.
        menu_image (Optional[pygame.Surface]): Imagen de fondo del menú.
        server_connected (bool): Estado de conexión con el servidor.
        players_ready (bool): Estado de preparación de jugadores.
        music_muted (bool): Estado de silencio de la música.
        connect_button (Dict[str, Any]): Configuración del botón de conexión.
        start_button (Dict[str, Any]): Configuración del botón de inicio.
        mute_button (Dict[str, Any]): Configuración del botón de música.
        buttons (List[Dict[str, Any]]): Lista de botones principales.
        font (pygame.font.Font): Fuente para texto de botones.
        mute_font (pygame.font.Font): Fuente para botón de música.
    """
    def __init__(self, screen: pygame.Surface) -> None:
        """Inicializar la pantalla del menú.
        
        Args:
            screen (pygame.Surface): Superficie de pantalla principal.
        """
        self._initialize_screen_properties(screen)
        self.load_assets()
        self._initialize_menu_states()
        self.setup_buttons()
        
    def _initialize_screen_properties(self, screen: pygame.Surface) -> None:
        """Inicializar propiedades de la pantalla.
        
        Args:
            screen (pygame.Surface): Superficie de pantalla principal.
        """
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        
    def _initialize_menu_states(self) -> None:
        """Inicializar estados del menú."""
        self.server_connected = MENU_STATE_DISCONNECTED
        self.players_ready = MENU_STATE_PLAYERS_NOT_READY
        self.music_muted = MENU_STATE_DISCONNECTED
        
    def load_assets(self) -> None:
        """Cargar recursos del menú."""
        try:
            self._load_menu_background()
        except pygame.error:
            self._handle_asset_loading_error()
            
    def _load_menu_background(self) -> None:
        """Cargar imagen de fondo del menú."""
        menu_path = os.path.join("assets", "images", "menu.png")
        self.menu_image = pygame.image.load(menu_path)
        self.menu_image = pygame.transform.scale(self.menu_image, (self.width, self.height))
        
    def _handle_asset_loading_error(self) -> None:
        """Manejar error de carga de recursos."""
        self.menu_image = None
        print(MENU_TEXT['ASSET_ERROR'])
    
    def setup_buttons(self) -> None:
        """Configurar todos los botones del menú."""
        self._setup_main_buttons()
        self._setup_mute_button()
        self._setup_button_list_and_fonts()
        
    def _setup_main_buttons(self) -> None:
        """Configurar botones principales de conexión e inicio."""
        center_x = self.width // MENU_BUTTON_DIVISION_FACTOR
        self.connect_button = self._create_connect_button(center_x)
        self.start_button = self._create_start_button(center_x)
        
    def _create_connect_button(self, center_x: int) -> Dict[str, Any]:
        """Crear botón de conexión.
        
        Args:
            center_x (int): Posición X del centro.
            
        Returns:
            Dict[str, Any]: Configuración del botón de conexión.
        """
        return {
            'rect': pygame.Rect(center_x - MENU_BUTTON_WIDTH // MENU_BUTTON_DIVISION_FACTOR, 
                              MENU_BUTTON_Y_CONNECT, MENU_BUTTON_WIDTH, MENU_BUTTON_HEIGHT),
            'text': MENU_TEXT['CONNECT_DEFAULT'],
            'enabled': True,
            'color': COLOR_BUTTON_CONNECT,
            'hover_color': COLOR_BUTTON_CONNECT_HOVER,
            'text_color': COLOR_WHITE
        }
        
    def _create_start_button(self, center_x: int) -> Dict[str, Any]:
        """Crear botón de inicio de partida.
        
        Args:
            center_x (int): Posición X del centro.
            
        Returns:
            Dict[str, Any]: Configuración del botón de inicio.
        """
        return {
            'rect': pygame.Rect(center_x - MENU_BUTTON_WIDTH // MENU_BUTTON_DIVISION_FACTOR, 
                              MENU_BUTTON_Y_START, MENU_BUTTON_WIDTH, MENU_BUTTON_HEIGHT),
            'text': MENU_TEXT['START_GAME'],
            'enabled': False,
            'color': COLOR_BUTTON_START,
            'hover_color': COLOR_BUTTON_START_HOVER,
            'disabled_color': COLOR_BUTTON_DISABLED,
            'text_color': COLOR_WHITE
        }
        
    def _setup_mute_button(self) -> None:
        """Configurar botón de control de música."""
        self.mute_button = {
            'rect': pygame.Rect(self.width - MUTE_BUTTON_WIDTH - MUTE_BUTTON_MARGIN, 
                              MUTE_BUTTON_MARGIN, MUTE_BUTTON_WIDTH, MUTE_BUTTON_HEIGHT),
            'text': MENU_TEXT['MUTE_MUSIC'],
            'text_muted': MENU_TEXT['UNMUTE_MUSIC'],
            'color': COLOR_BUTTON_MUTE,
            'hover_color': COLOR_BUTTON_MUTE_HOVER,
            'text_color': COLOR_WHITE
        }
        
    def _setup_button_list_and_fonts(self) -> None:
        """Configurar lista de botones y fuentes."""
        self.buttons = [self.connect_button, self.start_button]
        self.font = pygame.font.Font(MENU_FONT_SIZE_DEFAULT, FONT_SIZE_NORMAL)
        self.mute_font = pygame.font.Font(MENU_FONT_SIZE_DEFAULT, FONT_SIZE_SMALL)
        
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Manejar eventos de la pantalla del menú.
        
        Args:
            event (pygame.event.Event): Evento de pygame.
            
        Returns:
            Optional[str]: Acción a realizar o None si no hay acción.
        """
        if self._is_left_mouse_click(event):
            return self._handle_mouse_click()
        return None
        
    def _is_left_mouse_click(self, event: pygame.event.Event) -> bool:
        """Verificar si es un clic izquierdo del ratón.
        
        Args:
            event (pygame.event.Event): Evento a verificar.
            
        Returns:
            bool: True si es un clic izquierdo, False en caso contrario.
        """
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == MOUSE_BUTTON_LEFT
        
    def _handle_mouse_click(self) -> Optional[str]:
        """Manejar clic del ratón en botones.
        
        Returns:
            Optional[str]: Acción del botón clickeado o None.
        """
        mouse_pos = pygame.mouse.get_pos()
        
        if self._is_button_clicked(self.connect_button, mouse_pos):
            return MENU_EVENTS['CONNECT']
            
        if self._is_button_clicked(self.start_button, mouse_pos):
            return MENU_EVENTS['START_GAME']
            
        if self.mute_button['rect'].collidepoint(mouse_pos):
            return MENU_EVENTS['TOGGLE_MUSIC']
            
        return None
        
    def _is_button_clicked(self, button: Dict[str, Any], mouse_pos: Tuple[int, int]) -> bool:
        """Verificar si un botón fue clickeado y está habilitado.
        
        Args:
            button (Dict[str, Any]): Botón a verificar.
            mouse_pos (Tuple[int, int]): Posición del ratón.
            
        Returns:
            bool: True si el botón fue clickeado y está habilitado.
        """
        return button['rect'].collidepoint(mouse_pos) and button['enabled']
    
    def update(self) -> None:
        """Actualizar estado de los botones basado en conexión."""
        # Método mantenido para compatibilidad, la lógica se maneja en draw
        pass
    
    def draw_background(self) -> None:
        """Dibujar fondo del menú."""
        if self.menu_image:
            self.screen.blit(self.menu_image, (0, 0))
        else:
            self.screen.fill(MENU_BACKGROUND_COLOR_DEFAULT)

    def draw_button(self, button: Dict[str, Any], color: Tuple[int, int, int]) -> None:
        """Dibujar un botón en pantalla.
        
        Args:
            button (Dict[str, Any]): Configuración del botón.
            color (Tuple[int, int, int]): Color del botón.
        """
        pygame.draw.rect(self.screen, color, button['rect'])
        pygame.draw.rect(self.screen, COLOR_WHITE, button['rect'], MENU_BUTTON_BORDER_WIDTH)
        self._draw_button_text(button)
        
    def _draw_button_text(self, button: Dict[str, Any]) -> None:
        """Dibujar texto de un botón.
        
        Args:
            button (Dict[str, Any]): Configuración del botón.
        """
        text_surface = self.font.render(button['text'], True, button['text_color'])
        text_rect = text_surface.get_rect(center=button['rect'].center)
        self.screen.blit(text_surface, text_rect)

    def update_connection_status(self) -> Tuple[str, Tuple[int, int, int]]:
        """Actualizar estado de botones y texto según conexión.
        
        Returns:
            Tuple[str, Tuple[int, int, int]]: Texto de estado y color.
        """
        return self._get_connected_status() if self.server_connected else self._get_disconnected_status()
            
    def _get_connected_status(self) -> Tuple[str, Tuple[int, int, int]]:
        """Obtener estado cuando está conectado.
        
        Returns:
            Tuple[str, Tuple[int, int, int]]: Texto de estado y color.
        """
        self._update_connect_button_connected()
        
        return self._get_players_ready_status() if self.players_ready else self._get_waiting_players_status()
            
    def _update_connect_button_connected(self) -> None:
        """Actualizar botón de conexión cuando está conectado."""
        self.connect_button['text'] = MENU_TEXT['CONNECT_CONNECTED']
        self.connect_button['enabled'] = False
        self.connect_button['color'] = COLOR_BUTTON_CONNECT_ACTIVE
        
    def _get_players_ready_status(self) -> Tuple[str, Tuple[int, int, int]]:
        """Obtener estado cuando los jugadores están listos.
        
        Returns:
            Tuple[str, Tuple[int, int, int]]: Texto de estado y color.
        """
        self.start_button['enabled'] = True
        return MENU_TEXT['STATUS_READY'], COLOR_GREEN
        
    def _get_waiting_players_status(self) -> Tuple[str, Tuple[int, int, int]]:
        """Obtener estado esperando jugadores.
        
        Returns:
            Tuple[str, Tuple[int, int, int]]: Texto de estado y color.
        """
        self.start_button['enabled'] = False
        return MENU_TEXT['STATUS_CONNECTING'], COLOR_YELLOW
        
    def _get_disconnected_status(self) -> Tuple[str, Tuple[int, int, int]]:
        """Obtener estado cuando está desconectado.
        
        Returns:
            Tuple[str, Tuple[int, int, int]]: Texto de estado y color.
        """
        self.connect_button['text'] = MENU_TEXT['CONNECT_DEFAULT']
        self.connect_button['enabled'] = True
        self.connect_button['color'] = COLOR_BUTTON_CONNECT
        self.start_button['enabled'] = False
        return MENU_TEXT['STATUS_DISCONNECTED'], MENU_STATUS_COLOR_DISCONNECTED

    def render_all_buttons(self, mouse_pos: Tuple[int, int]) -> None:
        """Renderizar todos los botones del menú.
        
        Args:
            mouse_pos (Tuple[int, int]): Posición actual del ratón.
        """
        for button in self.buttons:
            color = self._get_button_color(button, mouse_pos)
            self.draw_button(button, color)
            
    def _get_button_color(self, button: Dict[str, Any], mouse_pos: Tuple[int, int]) -> Tuple[int, int, int]:
        """Obtener color apropiado para un botón.
        
        Args:
            button (Dict[str, Any]): Configuración del botón.
            mouse_pos (Tuple[int, int]): Posición del ratón.
            
        Returns:
            Tuple[int, int, int]: Color RGB del botón.
        """
        if not button['enabled']:
            return button.get('disabled_color', (100, 100, 100))
        
        return button['hover_color'] if button['rect'].collidepoint(mouse_pos) else button['color']

    def draw(self) -> None:
        """Dibujar toda la pantalla del menú."""
        self.draw_background()
        
        mouse_pos = pygame.mouse.get_pos()
        self.render_all_buttons(mouse_pos)
        
        self._draw_connection_status()
        self.draw_mute_button(mouse_pos)
        
    def _draw_connection_status(self) -> None:
        """Dibujar estado de conexión en pantalla."""
        status_text, status_color = self.update_connection_status()
        
        status_font = pygame.font.Font(MENU_FONT_SIZE_DEFAULT, FONT_SIZE_NORMAL)
        status_surface = status_font.render(status_text, True, status_color)
        status_rect = status_surface.get_rect(center=(self.width // MENU_BUTTON_DIVISION_FACTOR, MENU_STATUS_Y))
        self.screen.blit(status_surface, status_rect)
        
    
    def draw_mute_button(self, mouse_pos: Tuple[int, int]) -> None:
        """Dibujar el botón de control de música.
        
        Args:
            mouse_pos (Tuple[int, int]): Posición actual del ratón.
        """
        color = self._get_mute_button_color(mouse_pos)
        self._draw_mute_button_rectangle(color)
        self._draw_mute_button_text()
        
    def _get_mute_button_color(self, mouse_pos: Tuple[int, int]) -> Tuple[int, int, int]:
        """Obtener color del botón de música.
        
        Args:
            mouse_pos (Tuple[int, int]): Posición del ratón.
            
        Returns:
            Tuple[int, int, int]: Color RGB del botón.
        """
        return (self.mute_button['hover_color'] 
                if self.mute_button['rect'].collidepoint(mouse_pos) 
                else self.mute_button['color'])
            
    def _draw_mute_button_rectangle(self, color: Tuple[int, int, int]) -> None:
        """Dibujar rectángulo del botón de música.
        
        Args:
            color (Tuple[int, int, int]): Color del botón.
        """
        pygame.draw.rect(self.screen, color, self.mute_button['rect'])
        pygame.draw.rect(self.screen, COLOR_WHITE, self.mute_button['rect'], MUTE_BUTTON_BORDER_WIDTH)
        
    def _draw_mute_button_text(self) -> None:
        """Dibujar texto del botón de música."""
        text = self._get_mute_button_text()
        text_surface = self.mute_font.render(text, True, self.mute_button['text_color'])
        text_rect = text_surface.get_rect(center=self.mute_button['rect'].center)
        self.screen.blit(text_surface, text_rect)
        
    def _get_mute_button_text(self) -> str:
        """Obtener texto apropiado para el botón de música.
        
        Returns:
            str: Texto apropiado para el botón.
        """
        return self.mute_button['text_muted'] if self.music_muted else self.mute_button['text']
    
    def toggle_music_mute(self) -> None:
        """Alternar entre silenciar y reproducir la música."""
        self.music_muted = not self.music_muted
        self._apply_music_volume()
        self._print_music_status()
        
    def _apply_music_volume(self) -> None:
        """Aplicar volumen de música según estado."""
        volume = MUTED_VOLUME if self.music_muted else MUSIC_VOLUME_MENU
        pygame.mixer.music.set_volume(volume)
        
    def _print_music_status(self) -> None:
        """Imprimir estado actual de la música."""
        status = MENU_TEXT['MUSIC_MUTED'] if self.music_muted else MENU_TEXT['MUSIC_UNMUTED']
        print(status)
    
    def set_connection_status(self, connected: bool, players_ready: bool = False) -> None:
        """Actualizar el estado de conexión desde el cliente principal.
        
        Args:
            connected (bool): Estado de conexión con el servidor.
            players_ready (bool): Estado de preparación de jugadores.
        """
        self.server_connected = connected
        self.players_ready = players_ready