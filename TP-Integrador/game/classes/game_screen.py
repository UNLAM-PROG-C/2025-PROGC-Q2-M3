"""Módulo de la pantalla principal del juego de Batalla Naval.

Este módulo contiene la implementación de GameScreen que maneja
la colocación de barcos, la fase de batalla, y toda la lógica
de la interfaz principal del juego.
"""

import pygame
import os
import sys
from typing import Optional, Dict, Any, List, Tuple

# Importar constants y GameBoard desde las ubicaciones correctas
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from constants import (SHIP_SIZES, FONT_SIZE_NORMAL, FONT_SIZE_TITLE, FONT_SIZE_BOARD_TITLE, COLOR_WHITE, GAME_TITLE_SPACE, GAME_BOARD_TITLE_SPACE,
                      GAME_INFO_SPACE, GAME_SCREEN_MARGIN, GAME_BOARD_SPACING, GAME_BOARD_SIZE_REDUCTION_FACTOR,
                      GAME_SCREEN_DIVISION_FACTOR, GAME_PHASE_PLACEMENT, GAME_PHASE_WAITING_BATTLE,
                      GAME_PHASE_BATTLE, DEFAULT_SHIP_SIZE, SHIP_HORIZONTAL_DEFAULT, INITIAL_SHIP_INDEX,
                      PANEL_PADDING, COORD_SPACE, TITLE_SPACING, GAME_PANEL_ALPHA, MY_PANEL_COLOR,
                      ENEMY_PANEL_COLOR, PANEL_BORDER_WIDTH, INFO_PANEL_HEIGHT, INFO_PANEL_MARGIN,
                      INFO_PANEL_SIDE_MARGIN, INFO_PANEL_ALPHA, INFO_PANEL_COLOR, SHIPS_PANEL_WIDTH,
                      SHIPS_PANEL_HEIGHT, SHIPS_PANEL_X_MARGIN, SHIPS_PANEL_Y_OFFSET, SHIPS_PANEL_ALPHA,
                      MY_SHIPS_PANEL_COLOR, ENEMY_SHIPS_PANEL_COLOR, SHIPS_PANEL_BORDER_WIDTH,
                      OCEAN_COLOR_TOP, OCEAN_COLOR_BOTTOM, SHIP_PREVIEW_ALPHA, SHIP_PREVIEW_COLOR_VALID,
                      SHIP_PREVIEW_COLOR_INVALID, MOUSE_LEFT_BUTTON, MOUSE_RIGHT_BUTTON, KEY_ROTATE,
                      MISSILE_SOUND_VOLUME, WATER_SPLASH_VOLUME, GAME_TEXT, SOUND_PATHS,
                      SHIP_STATUS_COLORS, GAME_FONT_SIZES, EXPECTED_ENEMY_SHIPS, SHOT_RESULTS)
from .game_board import GameBoard

class GameScreen:
    """Pantalla principal del juego de Batalla Naval.
    
    Esta clase maneja toda la lógica de la pantalla principal del juego,
    incluyendo la colocación de barcos, la fase de batalla, el manejo de
    eventos, el renderizado de tableros y la gestión de estado del juego.
    
    Attributes:
        screen (pygame.Surface): Superficie de pantalla principal.
        width (int): Ancho de la pantalla.
        height (int): Alto de la pantalla.
        network_manager (Optional): Gestor de red para comunicación.
        my_board (GameBoard): Tablero del jugador.
        enemy_board (GameBoard): Tablero del enemigo.
        game_phase (str): Fase actual del juego.
        selected_ship_size (int): Tamaño del barco seleccionado.
        ship_horizontal (bool): Orientación del barco.
        my_turn (bool): Indicador de turno del jugador.
        ships_to_place (List[int]): Lista de barcos por colocar.
        current_ship_index (int): Índice del barco actual.
        enemy_sunk_ships (List[str]): Lista de barcos enemigos hundidos.
        enemy_sunk_ships_info (Dict): Información de barcos enemigos hundidos.
        font (pygame.font.Font): Fuente para texto.
    """
    def __init__(self, screen: pygame.Surface, network_manager: Optional[Any] = None) -> None:
        """Inicializar la pantalla de juego.
        
        Args:
            screen (pygame.Surface): Superficie de pantalla principal.
            network_manager (Optional[Any]): Gestor de red para comunicación.
        """
        self._initialize_screen_properties(screen, network_manager)
        self._calculate_board_dimensions()
        self._setup_game_boards()
        self._initialize_game_state()
        self._initialize_ship_tracking()
        self._setup_fonts()
        print(GAME_TEXT['REALISTIC_SHIPS_INIT'])
        
    def _initialize_screen_properties(self, screen: pygame.Surface, network_manager: Optional[Any]) -> None:
        """Inicializar propiedades básicas de la pantalla.
        
        Args:
            screen (pygame.Surface): Superficie de pantalla principal.
            network_manager (Optional[Any]): Gestor de red.
        """
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.network_manager = network_manager
        
    def _calculate_board_dimensions(self) -> None:
        """Calcular dimensiones y posiciones de los tableros."""
        available_height = self.height - GAME_TITLE_SPACE - GAME_BOARD_TITLE_SPACE - GAME_INFO_SPACE
        available_width = self.width - GAME_SCREEN_MARGIN
        
        max_board_width = (available_width - GAME_BOARD_SPACING) // GAME_SCREEN_DIVISION_FACTOR
        max_board_height = available_height
        
        self.board_size = int(min(max_board_width, max_board_height) * GAME_BOARD_SIZE_REDUCTION_FACTOR)
        self.start_x = self._calculate_board_start_x()
        self.board_y = self._calculate_board_y()
        
    def _calculate_board_start_x(self) -> int:
        """Calcular posición X inicial de los tableros.
        
        Returns:
            int: Posición X inicial.
        """
        total_width = self.board_size * GAME_SCREEN_DIVISION_FACTOR + GAME_BOARD_SPACING
        return (self.width - total_width) // GAME_SCREEN_DIVISION_FACTOR
        
    def _calculate_board_y(self) -> int:
        """Calcular posición Y de los tableros.
        
        Returns:
            int: Posición Y de los tableros.
        """
        total_board_area = self.board_size + GAME_BOARD_TITLE_SPACE
        available_vertical = self.height - GAME_TITLE_SPACE - GAME_INFO_SPACE
        return GAME_TITLE_SPACE + (available_vertical - total_board_area) // GAME_SCREEN_DIVISION_FACTOR + GAME_BOARD_TITLE_SPACE
        
    def _setup_game_boards(self) -> None:
        """Configurar los tableros de juego."""
        self.my_board = GameBoard(self.start_x, self.board_y, self.board_size)
        enemy_board_x = self.start_x + self.board_size + GAME_BOARD_SPACING
        self.enemy_board = GameBoard(enemy_board_x, self.board_y, self.board_size)
        
    def _initialize_game_state(self) -> None:
        """Inicializar estado del juego."""
        self.game_phase = GAME_PHASE_PLACEMENT
        self.selected_ship_size = DEFAULT_SHIP_SIZE
        self.ship_horizontal = SHIP_HORIZONTAL_DEFAULT
        self.my_turn = False
        self.ships_to_place = SHIP_SIZES.copy()
        self.current_ship_index = INITIAL_SHIP_INDEX
        
    def _initialize_ship_tracking(self) -> None:
        """Inicializar seguimiento de barcos enemigos."""
        self.enemy_sunk_ships: List[str] = []
        self.enemy_sunk_ships_info: Dict[Tuple[int, int], str] = {}
        
    def _setup_fonts(self) -> None:
        """Configurar fuentes del juego."""
        self.font = pygame.font.Font(None, FONT_SIZE_NORMAL)
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Manejar eventos de la pantalla de juego.
        
        Args:
            event (pygame.event.Event): Evento de pygame.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_event(event)
        elif event.type == pygame.KEYDOWN:
            self._handle_keyboard_event(event)
            
    def _handle_mouse_event(self, event: pygame.event.Event) -> None:
        """Manejar eventos de ratón.
        
        Args:
            event (pygame.event.Event): Evento de ratón.
        """
        if event.button == MOUSE_LEFT_BUTTON:
            self.handle_left_click(event.pos)
        elif event.button == MOUSE_RIGHT_BUTTON:
            self.handle_right_click(event.pos)
            
    def _handle_keyboard_event(self, event: pygame.event.Event) -> None:
        """Manejar eventos de teclado.
        
        Args:
            event (pygame.event.Event): Evento de teclado.
        """
        if event.key == KEY_ROTATE:
            self.ship_horizontal = not self.ship_horizontal
    
    def handle_left_click(self, mouse_pos: Tuple[int, int]) -> None:
        """Manejar clic izquierdo del ratón.
        
        Args:
            mouse_pos (Tuple[int, int]): Posición del ratón.
        """
        if self._is_placement_phase():
            self._handle_ship_placement(mouse_pos)
        elif self._is_battle_phase_my_turn():
            self._handle_battle_shot(mouse_pos)
            
    def _is_placement_phase(self) -> bool:
        """Verificar si estamos en fase de colocación.
        
        Returns:
            bool: True si estamos colocando barcos.
        """
        return (self.game_phase == GAME_PHASE_PLACEMENT and 
               self.current_ship_index < len(self.ships_to_place))
               
    def _is_battle_phase_my_turn(self) -> bool:
        """Verificar si es mi turno en fase de batalla.
        
        Returns:
            bool: True si es mi turno en batalla.
        """
        return self.game_phase == GAME_PHASE_BATTLE and self.my_turn
        
    def _handle_ship_placement(self, mouse_pos: Tuple[int, int]) -> None:
        """Manejar colocación de barcos.
        
        Args:
            mouse_pos (Tuple[int, int]): Posición del ratón.
        """
        cell = self.my_board.get_cell_from_mouse(mouse_pos)
        if cell:
            ship_size = self.ships_to_place[self.current_ship_index]
            if self.my_board.place_ship(ship_size, cell[0], cell[1], self.ship_horizontal):
                self._advance_ship_placement()
                
    def _advance_ship_placement(self) -> None:
        """Avanzar al siguiente barco en colocación."""
        self.current_ship_index += 1
        if self.current_ship_index >= len(self.ships_to_place):
            self.game_phase = GAME_PHASE_WAITING_BATTLE
            self.send_ships_to_server()
            
    def _handle_battle_shot(self, mouse_pos: Tuple[int, int]) -> None:
        """Manejar disparo en fase de batalla.
        
        Args:
            mouse_pos (Tuple[int, int]): Posición del ratón.
        """
        cell = self.enemy_board.get_cell_from_mouse(mouse_pos)
        if self._can_shoot_at_cell(cell):
            self.network_manager.make_shot(cell[0], cell[1])
            
    def _can_shoot_at_cell(self, cell: Optional[Tuple[int, int]]) -> bool:
        """Verificar si se puede disparar a una celda.
        
        Args:
            cell (Optional[Tuple[int, int]]): Celda objetivo.
            
        Returns:
            bool: True si se puede disparar.
        """
        return (cell is not None and 
               cell not in self.enemy_board.shots and 
               self.network_manager is not None)
    
    def handle_right_click(self, mouse_pos: Tuple[int, int]) -> None:
        """Manejar clic derecho del ratón.
        
        Args:
            mouse_pos (Tuple[int, int]): Posición del ratón.
        """
        self.ship_horizontal = not self.ship_horizontal
    
    def update(self) -> None:
        """Actualizar estado de la pantalla de juego."""
        pass
    
    def draw(self) -> None:
        """Dibujar toda la pantalla de juego."""
        self.draw_ocean_background()
        self.draw_board_panels()
        self._draw_game_title()
        self._draw_board_titles()
        self._draw_game_boards()
        self._draw_ship_preview_if_needed()
        self._draw_game_info()
        
    def _draw_game_title(self) -> None:
        """Dibujar título principal del juego."""
        title_font = pygame.font.Font(None, GAME_FONT_SIZES['TITLE'])
        title_text = title_font.render(GAME_TEXT['TITLE'], True, COLOR_WHITE)
        title_rect = title_text.get_rect(center=(self.width // GAME_SCREEN_DIVISION_FACTOR, 35))
        self.screen.blit(title_text, title_rect)
        
    def _draw_board_titles(self) -> None:
        """Dibujar títulos de los tableros."""
        board_font = pygame.font.Font(None, GAME_FONT_SIZES['BOARD_TITLE'])
        title_y = self._calculate_board_title_y()
        
        self._draw_my_board_title(board_font, title_y)
        self._draw_enemy_board_title(board_font, title_y)
        
    def _calculate_board_title_y(self) -> int:
        """Calcular posición Y de los títulos de tableros.
        
        Returns:
            int: Posición Y de los títulos.
        """
        panel_top = self.my_board.y - PANEL_PADDING - COORD_SPACE
        return panel_top - TITLE_SPACING
        
    def _draw_my_board_title(self, board_font: pygame.font.Font, title_y: int) -> None:
        """Dibujar título de mi tablero.
        
        Args:
            board_font (pygame.font.Font): Fuente para el título.
            title_y (int): Posición Y del título.
        """
        my_title = board_font.render(GAME_TEXT['MY_FLEET'], True, SHIP_STATUS_COLORS['WHITE'])
        center_x = self.my_board.x + self.my_board.width // GAME_SCREEN_DIVISION_FACTOR
        my_title_rect = my_title.get_rect(center=(center_x, title_y))
        self.screen.blit(my_title, my_title_rect)
        
    def _draw_enemy_board_title(self, board_font: pygame.font.Font, title_y: int) -> None:
        """Dibujar título del tablero enemigo.
        
        Args:
            board_font (pygame.font.Font): Fuente para el título.
            title_y (int): Posición Y del título.
        """
        enemy_title = board_font.render(GAME_TEXT['ENEMY'], True, SHIP_STATUS_COLORS['WHITE'])
        center_x = self.enemy_board.x + self.enemy_board.width // GAME_SCREEN_DIVISION_FACTOR
        enemy_title_rect = enemy_title.get_rect(center=(center_x, title_y))
        self.screen.blit(enemy_title, enemy_title_rect)
        
    def _draw_game_boards(self) -> None:
        """Dibujar tableros de juego."""
        self.my_board.draw(self.screen, show_ships=True)
        self.draw_enemy_board_with_sunk_ships()
        
        if self._should_show_ships_status():
            self.draw_ships_status()
            
    def _should_show_ships_status(self) -> bool:
        """Verificar si se debe mostrar el estado de los barcos.
        
        Returns:
            bool: True si se debe mostrar el estado.
        """
        return (self.game_phase == GAME_PHASE_BATTLE or 
               self.game_phase == GAME_PHASE_WAITING_BATTLE)
               
    def _draw_ship_preview_if_needed(self) -> None:
        """Dibujar vista previa del barco si es necesario."""
        if self._should_show_ship_preview():
            mouse_pos = pygame.mouse.get_pos()
            cell = self.my_board.get_cell_from_mouse(mouse_pos)
            if cell:
                self.draw_ship_preview_realistic(cell[0], cell[1])
                
    def _should_show_ship_preview(self) -> bool:
        """Verificar si se debe mostrar la vista previa del barco.
        
        Returns:
            bool: True si se debe mostrar vista previa.
        """
        return (self.game_phase == GAME_PHASE_PLACEMENT and 
               self.current_ship_index < len(self.ships_to_place))
        return panel_top - TITLE_SPACING
        
    def _draw_my_board_title(self, board_font: pygame.font.Font, title_y: int) -> None:
        """Dibujar título de mi tablero.
        
        Args:
            board_font (pygame.font.Font): Fuente para el título.
            title_y (int): Posición Y del título.
        """
        my_title = board_font.render(GAME_TEXT['MY_FLEET'], True, SHIP_STATUS_COLORS['WHITE'])
        center_x = self.my_board.x + self.my_board.width // GAME_SCREEN_DIVISION_FACTOR
        my_title_rect = my_title.get_rect(center=(center_x, title_y))
        self.screen.blit(my_title, my_title_rect)
        
    def _draw_enemy_board_title(self, board_font: pygame.font.Font, title_y: int) -> None:
        """Dibujar título del tablero enemigo.
        
        Args:
            board_font (pygame.font.Font): Fuente para el título.
            title_y (int): Posición Y del título.
        """
        enemy_title = board_font.render(GAME_TEXT['ENEMY'], True, SHIP_STATUS_COLORS['WHITE'])
        center_x = self.enemy_board.x + self.enemy_board.width // GAME_SCREEN_DIVISION_FACTOR
        enemy_title_rect = enemy_title.get_rect(center=(center_x, title_y))
        self.screen.blit(enemy_title, enemy_title_rect)
        
    def _draw_game_boards(self) -> None:
        """Dibujar tableros de juego."""
        self.my_board.draw(self.screen, show_ships=True)
        self.draw_enemy_board_with_sunk_ships()
        
        if self._should_show_ships_status():
            self.draw_ships_status()
            
    def _should_show_ships_status(self) -> bool:
        """Verificar si se debe mostrar el estado de los barcos.
        
        Returns:
            bool: True si se debe mostrar el estado.
        """
        return (self.game_phase == GAME_PHASE_BATTLE or 
               self.game_phase == GAME_PHASE_WAITING_BATTLE)
               
    def _draw_ship_preview_if_needed(self) -> None:
        """Dibujar vista previa del barco si es necesario."""
        if self._should_show_ship_preview():
            mouse_pos = pygame.mouse.get_pos()
            cell = self.my_board.get_cell_from_mouse(mouse_pos)
            if cell:
                self.draw_ship_preview_realistic(cell[0], cell[1])
                
    def _should_show_ship_preview(self) -> bool:
        """Verificar si se debe mostrar la vista previa del barco.
        
        Returns:
            bool: True si se debe mostrar vista previa.
        """
        return (self.game_phase == GAME_PHASE_PLACEMENT and 
               self.current_ship_index < len(self.ships_to_place))
               
    def _draw_game_info(self) -> None:
        """Dibujar información del juego."""
        self.draw_info_panel()
        self._draw_status_text()
        self._draw_additional_info()
        
    def _draw_status_text(self) -> None:
        """Dibujar texto de estado principal."""
        status_text = self._get_status_text()
        main_info_font = pygame.font.Font(None, GAME_FONT_SIZES['MAIN_INFO'])
        
        status_surface = main_info_font.render(status_text, True, SHIP_STATUS_COLORS['WHITE'])
        center_x = self.width // GAME_SCREEN_DIVISION_FACTOR
        status_rect = status_surface.get_rect(center=(center_x, self.height - 75))
        self.screen.blit(status_surface, status_rect)
        
    def _get_status_text(self) -> str:
        """Obtener texto de estado actual.
        
        Returns:
            str: Texto de estado del juego.
        """
        if self.game_phase == GAME_PHASE_PLACEMENT:
            return self._get_placement_status_text()
        elif self.game_phase == GAME_PHASE_BATTLE:
            return self._get_battle_status_text()
        elif self.game_phase == GAME_PHASE_WAITING_BATTLE:
            return GAME_TEXT['WAITING_BATTLE']
        else:
            return GAME_TEXT['PREPARING']
            
    def _get_placement_status_text(self) -> str:
        """Obtener texto de estado para fase de colocación.
        
        Returns:
            str: Texto de estado de colocación.
        """
        if self.current_ship_index < len(self.ships_to_place):
            ship_size = self.ships_to_place[self.current_ship_index]
            orientation = GAME_TEXT['HORIZONTAL'] if self.ship_horizontal else GAME_TEXT['VERTICAL']
            return GAME_TEXT['PLACING_SHIP'].format(ship_size, orientation)
        else:
            return GAME_TEXT['ALL_SHIPS_PLACED']
            
    def _get_battle_status_text(self) -> str:
        """Obtener texto de estado para fase de batalla.
        
        Returns:
            str: Texto de estado de batalla.
        """
        return GAME_TEXT['YOUR_TURN'] if self.my_turn else GAME_TEXT['OPPONENT_TURN']
            
    def _draw_additional_info(self) -> None:
        """Dibujar información adicional del juego."""
        if self.game_phase == GAME_PHASE_PLACEMENT:
            remaining_ships = self.ships_to_place[self.current_ship_index:]
            if remaining_ships:
                self._draw_remaining_ships_info(remaining_ships)
                
    def _draw_remaining_ships_info(self, remaining_ships: List[int]) -> None:
        """Dibujar información de barcos restantes.
        
        Args:
            remaining_ships (List[int]): Lista de barcos restantes.
        """
        ships_text = GAME_TEXT['REMAINING_SHIPS'].format(remaining_ships)
        secondary_info_font = pygame.font.Font(None, GAME_FONT_SIZES['SECONDARY_INFO'])
        
        ships_surface = secondary_info_font.render(ships_text, True, SHIP_STATUS_COLORS['LIGHT_BLUE'])
        center_x = self.width // GAME_SCREEN_DIVISION_FACTOR
        ships_rect = ships_surface.get_rect(center=(center_x, self.height - 45))
        self.screen.blit(ships_surface, ships_rect)

    
    def draw_ocean_background(self) -> None:
        """Dibujar fondo oceánico con gradiente."""
        for y in range(self.height):
            ratio = y / self.height
            color = self._calculate_ocean_color(ratio)
            pygame.draw.line(self.screen, color, (0, y), (self.width, y))
            
    def _calculate_ocean_color(self, ratio: float) -> Tuple[int, int, int]:
        """Calcular color del océano para gradiente.
        
        Args:
            ratio (float): Ratio de posición vertical (0-1).
            
        Returns:
            Tuple[int, int, int]: Color RGB calculado.
        """
        r = int(OCEAN_COLOR_TOP['r'] + (OCEAN_COLOR_BOTTOM['r'] - OCEAN_COLOR_TOP['r']) * ratio)
        g = int(OCEAN_COLOR_TOP['g'] + (OCEAN_COLOR_BOTTOM['g'] - OCEAN_COLOR_TOP['g']) * ratio)
        b = int(OCEAN_COLOR_TOP['b'] + (OCEAN_COLOR_BOTTOM['b'] - OCEAN_COLOR_TOP['b']) * ratio)
        return (r, g, b)
    
    def draw_board_panels(self) -> None:
        """Dibujar paneles de fondo para los tableros."""
        self._draw_my_board_panel()
        self._draw_enemy_board_panel()
        self._draw_panel_borders()
        
    def _draw_my_board_panel(self) -> None:
        """Dibujar panel de fondo para mi tablero."""
        my_panel_rect = self._calculate_my_panel_rect()
        my_panel_surface = self._create_panel_surface(my_panel_rect, MY_PANEL_COLOR)
        self.screen.blit(my_panel_surface, (my_panel_rect.x, my_panel_rect.y))
        
    def _draw_enemy_board_panel(self) -> None:
        """Dibujar panel de fondo para tablero enemigo."""
        enemy_panel_rect = self._calculate_enemy_panel_rect()
        enemy_panel_surface = self._create_panel_surface(enemy_panel_rect, ENEMY_PANEL_COLOR)
        self.screen.blit(enemy_panel_surface, (enemy_panel_rect.x, enemy_panel_rect.y))
        
    def _calculate_my_panel_rect(self) -> pygame.Rect:
        """Calcular rectángulo del panel de mi tablero.
        
        Returns:
            pygame.Rect: Rectángulo del panel.
        """
        return pygame.Rect(
            self.my_board.x - PANEL_PADDING - COORD_SPACE,
            self.my_board.y - PANEL_PADDING - COORD_SPACE,
            self.my_board.width + PANEL_PADDING * 2 + COORD_SPACE * 2,
            self.my_board.height + PANEL_PADDING * 2 + COORD_SPACE * 2
        )
        
    def _calculate_enemy_panel_rect(self) -> pygame.Rect:
        """Calcular rectángulo del panel del tablero enemigo.
        
        Returns:
            pygame.Rect: Rectángulo del panel enemigo.
        """
        return pygame.Rect(
            self.enemy_board.x - PANEL_PADDING - COORD_SPACE,
            self.enemy_board.y - PANEL_PADDING - COORD_SPACE,
            self.enemy_board.width + PANEL_PADDING * 2 + COORD_SPACE * 2,
            self.enemy_board.height + PANEL_PADDING * 2 + COORD_SPACE * 2
        )
        
    def _create_panel_surface(self, panel_rect: pygame.Rect, color: Tuple[int, int, int]) -> pygame.Surface:
        """Crear superficie del panel con transparencia.
        
        Args:
            panel_rect (pygame.Rect): Rectángulo del panel.
            color (Tuple[int, int, int]): Color del panel.
            
        Returns:
            pygame.Surface: Superficie del panel.
        """
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height))
        panel_surface.set_alpha(GAME_PANEL_ALPHA)
        panel_surface.fill(color)
        return panel_surface
        
    def _draw_panel_borders(self) -> None:
        """Dibujar bordes de los paneles."""
        my_panel_rect = self._calculate_my_panel_rect()
        enemy_panel_rect = self._calculate_enemy_panel_rect()
        
        pygame.draw.rect(self.screen, (100, 149, 237), my_panel_rect, PANEL_BORDER_WIDTH)
        pygame.draw.rect(self.screen, (220, 20, 60), enemy_panel_rect, PANEL_BORDER_WIDTH)
    
    def draw_info_panel(self):
        panel_height = 110
        panel_y = self.height - panel_height - 15
        
        info_panel = pygame.Rect(60, panel_y, self.width - 120, panel_height)
        info_surface = pygame.Surface((info_panel.width, info_panel.height))
        info_surface.set_alpha(130)
        info_surface.fill((25, 45, 85))
        
        self.screen.blit(info_surface, (info_panel.x, info_panel.y))
        pygame.draw.rect(self.screen, (120, 160, 255), info_panel, 3)
    
    def draw_ships_status(self):
        """Dibujar el estado de los barcos propios y enemigos"""
        ship_font = pygame.font.Font(None, 24)
        title_font = pygame.font.Font(None, 28)
        
        # Panel izquierdo para barcos propios
        left_panel_x = 10
        left_panel_y = self.my_board.y + 50
        left_panel_width = 200
        left_panel_height = 300
        
        # Panel derecho para barcos enemigos
        right_panel_x = self.width - 210
        right_panel_y = self.enemy_board.y + 50
        right_panel_width = 200
        right_panel_height = 300
        
        # Dibujar panel de mis barcos
        left_panel = pygame.Rect(left_panel_x, left_panel_y, left_panel_width, left_panel_height)
        left_surface = pygame.Surface((left_panel_width, left_panel_height))
        left_surface.set_alpha(180)
        left_surface.fill((20, 60, 40))
        self.screen.blit(left_surface, (left_panel_x, left_panel_y))
        pygame.draw.rect(self.screen, (100, 200, 120), left_panel, 2)
        
        # Título panel izquierdo
        my_title = title_font.render("MIS BARCOS", True, (255, 255, 255))
        self.screen.blit(my_title, (left_panel_x + 10, left_panel_y + 10))
        
        # Estado de mis barcos
        my_ships = self.my_board.get_ships_status()
        y_offset = 40
        for ship in my_ships:
            if ship['sunk']:
                color = (255, 100, 100)  # Rojo para hundidos
                status = "HUNDIDO"
            else:
                color = (100, 255, 100)  # Verde para activos
                status = f"{ship['hits']}/{ship['total_hits_needed']} impactos"
            
            ship_text = ship_font.render(f"• {ship['name']}", True, color)
            status_text = ship_font.render(f"  {status}", True, (200, 200, 200))
            
            self.screen.blit(ship_text, (left_panel_x + 10, left_panel_y + y_offset))
            self.screen.blit(status_text, (left_panel_x + 15, left_panel_y + y_offset + 18))
            y_offset += 45
        
        # Dibujar panel de barcos enemigos
        right_panel = pygame.Rect(right_panel_x, right_panel_y, right_panel_width, right_panel_height)
        right_surface = pygame.Surface((right_panel_width, right_panel_height))
        right_surface.set_alpha(180)
        right_surface.fill((60, 20, 20))
        self.screen.blit(right_surface, (right_panel_x, right_panel_y))
        pygame.draw.rect(self.screen, (200, 100, 100), right_panel, 2)
        
        # Título panel derecho
        enemy_title = title_font.render("BARCOS ENEMIGOS", True, (255, 255, 255))
        self.screen.blit(enemy_title, (right_panel_x + 10, right_panel_y + 10))
        
        # Estado de barcos enemigos (estimado basado en los hundidos conocidos)
        enemy_ships = self.get_enemy_ships_status()
        y_offset = 40
        for ship in enemy_ships:
            if ship['sunk']:
                color = (255, 100, 100)  # Rojo para hundidos
                status = "HUNDIDO"
            else:
                color = (255, 200, 100)  # Amarillo para desconocidos
                status = "ACTIVO"
            
            ship_text = ship_font.render(f"• {ship['name']}", True, color)
            status_text = ship_font.render(f"  {status}", True, (200, 200, 200))
            
            self.screen.blit(ship_text, (right_panel_x + 10, right_panel_y + y_offset))
            self.screen.blit(status_text, (right_panel_x + 15, right_panel_y + y_offset + 18))
            y_offset += 45
    
    def get_enemy_ships_status(self):
        """Obtener el estado estimado de los barcos enemigos"""
        # Lista de barcos que debería tener el enemigo
        expected_ships = [
            {"name": "Portaaviones", "size": 5, "sunk": False},
            {"name": "Destructor Acorazado", "size": 4, "sunk": False},
            {"name": "Barco de Ataque #1", "size": 3, "sunk": False},
            {"name": "Barco de Ataque #2", "size": 3, "sunk": False},
            {"name": "Lancha Rapida", "size": 2, "sunk": False}
        ]
        
        # Marcar como hundidos los barcos que están en nuestra lista
        for sunk_ship_name in self.enemy_sunk_ships:
            for ship in expected_ships:
                if ship['name'] == sunk_ship_name or (sunk_ship_name == "Barco de Ataque" and "Barco de Ataque" in ship['name'] and not ship['sunk']):
                    ship['sunk'] = True
                    break
        
        return expected_ships
    
    def draw_ship_preview_realistic(self, x, y):
        from .ship import Ship  # Import local para evitar dependencia circular
        
        ship_size = self.ships_to_place[self.current_ship_index]
        
        can_place = self.my_board.can_place_ship(ship_size, x, y, self.ship_horizontal)
        
        temp_ship = Ship(ship_size)
        temp_ship.horizontal = self.ship_horizontal
        
        for i in range(ship_size):
            if self.ship_horizontal:
                temp_ship.positions.append((x + i, y))
            else:
                temp_ship.positions.append((x, y + i))
        
        preview_surface = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        preview_surface.set_alpha(60)  # Reducido de 120 a 60 para menos transparencia/oscuridad
        preview_surface.fill((0, 0, 0, 0))
        
        temp_board = GameBoard(self.my_board.x, self.my_board.y, self.my_board.width)
        temp_board.ships = [temp_ship]
        temp_board.colors = self.my_board.colors.copy()
        
        if can_place:
            temp_board.colors['ship'] = (0, 255, 0)  # Verde más brillante
        else:
            temp_board.colors['ship'] = (255, 50, 50)  # Rojo más brillante
        
        temp_board.draw_realistic_ship(preview_surface, temp_ship)
        
        self.screen.blit(preview_surface, (0, 0))
    
    def send_ships_to_server(self):
        if self.network_manager:
            ships_data = []
            for ship in self.my_board.ships:
                ships_data.append(ship.positions)
            
            self.network_manager.place_ships(ships_data)
            print("Barcos enviados al servidor")
    
    def handle_shot_result(self, data):
        x, y = data.get('x'), data.get('y')
        result = data.get('result')
        shooter = data.get('shooter')
        ship_info = data.get('ship_info')  # Información del barco hundido (si aplica)
        
        print(f"Disparo en ({x}, {y}) por jugador {shooter}: {result}")
        
        # Extraer nombre del barco si fue hundido
        sunk_ship_name = None
        if result == 'sunk' and ship_info:
            sunk_ship_name = ship_info.get('name')
            ship_size = ship_info.get('size')
            ship_positions = ship_info.get('positions', [])
            print(f"📊 Información del barco hundido: {sunk_ship_name} (tamaño: {ship_size})")

        if result == 'hit' or result == 'sunk':
            self.play_missile_sound()
        elif result == 'miss':
            self.play_water_splash_sound()
        
        if shooter == self.network_manager.player_id:
            # Mi disparo - registrar en el tablero enemigo
            self.enemy_board.shots[(x, y)] = result
            
            # Si hundí un barco enemigo, procesarlo completamente
            if result == 'sunk' and sunk_ship_name and ship_info:
                # Allow storing multiple sunk ships even if they have the same name
                # (e.g. two "Barco de Ataque"). We intentionally don't deduplicate by name.
                self.enemy_sunk_ships.append(sunk_ship_name)
                print(f"🎯 ¡HUNDISTE EL {sunk_ship_name.upper()} ENEMIGO!")

                # Almacenar información completa del barco para mostrar nombres en el tablero
                ship_positions = ship_info.get('positions', [])
                for pos in ship_positions:
                    self.enemy_sunk_ships_info[tuple(pos)] = sunk_ship_name

                # Marcar todas las posiciones del barco como hundidas (usar posiciones reales)
                self.enemy_board.mark_enemy_ship_sunk(ship_info, ship_positions)
            
            # Solo pierdo el turno si es miss
            if result == 'miss':
                self.my_turn = False
            # Si es hit o sunk, mantengo el turno para seguir disparando
            
        else:
            # El disparo fue del oponente hacia mi tablero
            # Registrar el disparo del enemigo en mi tablero propio
            self.my_board.shots[(x, y)] = result
            
            # Si fue hit, también marcar el barco como golpeado
            if result == 'hit' or result == 'sunk':
                for ship in self.my_board.ships:
                    if (x, y) in ship.positions:
                        ship.hit(x, y)
                        if ship.sunk and result == 'sunk':
                            print(f"💥 ¡El enemigo hundió tu {ship.name}!")
                        break
    
    def set_my_turn(self, is_my_turn):
        self.my_turn = is_my_turn
    
    def start_battle_phase(self):
        print("🚀 Iniciando fase de batalla...")
        self.game_phase = "battle"
    

    
    def draw_enemy_board_with_sunk_ships(self):
        """Dibujar el tablero enemigo sin etiquetas de barcos hundidos"""
        # Simplemente dibujar el tablero normal sin etiquetas
        self.enemy_board.draw(self.screen, show_ships=False)
    
    def play_missile_sound(self):
        """Reproducir sonido de impacto de misil"""
        try:
            missile_sound_path = os.path.join("assets", "sounds", "misil.mp3")
            missile_sound = pygame.mixer.Sound(missile_sound_path)
            missile_sound.set_volume(0.3)  # Volumen reducido al 30% para evitar saturación
            missile_sound.play()
            print("🔊 Reproduciendo sonido de impacto de misil")
        except pygame.error as e:
            print(f"❌ Error al reproducir sonido de misil: {e}")
        except FileNotFoundError:
            print("❌ No se encontró el archivo misil.mp3")
    
    def play_water_splash_sound(self):
        """Reproducir sonido de salpicadura de agua cuando se falla"""
        try:
            splash_sound_path = os.path.join("assets", "sounds", "waterSplash.mp3")
            splash_sound = pygame.mixer.Sound(splash_sound_path)
            splash_sound.set_volume(0.25)  # Volumen reducido al 25% para evitar saturación
            splash_sound.play()
            print("🔊 Reproduciendo sonido de salpicadura de agua")
        except pygame.error as e:
            print(f"❌ Error al reproducir sonido de salpicadura: {e}")
        except FileNotFoundError:
            print("❌ No se encontró el archivo waterSplash.mp3")

    def reset_game_state(self):
        """Resetear el estado de la pantalla de juego para una nueva partida.

        Esto limpia tableros, barcos, disparos y la información de barcos hundidos
        para evitar que queden residuos de la partida anterior en la UI.
        """
        # Reiniciar tableros completamente
        self.my_board = GameBoard(self.my_board.x, self.my_board.y, self.my_board.width)
        self.enemy_board = GameBoard(self.enemy_board.x, self.enemy_board.y, self.enemy_board.width)

        # Resetear estado de fase y colocación
        self.game_phase = "placement"
        self.selected_ship_size = 2
        self.ship_horizontal = True
        self.my_turn = False
        self.ships_to_place = [5, 4, 3, 3, 2]
        self.current_ship_index = 0

        # Limpiar seguimiento de barcos enemigos hundidos
        self.enemy_sunk_ships = []
        self.enemy_sunk_ships_info = {}

        # Fuentes se preservan
        print("🔄 Estado del juego reseteado para nueva partida")