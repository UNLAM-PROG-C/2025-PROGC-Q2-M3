import pygame
import os
import sys
import asyncio
from typing import Optional, Dict, Any, List, Tuple

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from constants import (SHIP_SIZES, FONT_SIZE_NORMAL, COLOR_WHITE, GAME_TITLE_SPACE, GAME_BOARD_TITLE_SPACE,
                      GAME_INFO_SPACE, GAME_SCREEN_MARGIN, GAME_BOARD_SPACING, GAME_BOARD_SIZE_REDUCTION_FACTOR,
                      GAME_SCREEN_DIVISION_FACTOR, GAME_PHASE_PLACEMENT, GAME_PHASE_WAITING_BATTLE,
                      GAME_PHASE_BATTLE, DEFAULT_SHIP_SIZE, SHIP_HORIZONTAL_DEFAULT, INITIAL_SHIP_INDEX,
                      PANEL_PADDING, COORD_SPACE, TITLE_SPACING, GAME_PANEL_ALPHA, MY_PANEL_COLOR,
                      ENEMY_PANEL_COLOR, PANEL_BORDER_WIDTH, OCEAN_COLOR_TOP, OCEAN_COLOR_BOTTOM,
                      MOUSE_LEFT_BUTTON, MOUSE_RIGHT_BUTTON, KEY_ROTATE, GAME_TEXT,
                      SHIP_STATUS_COLORS, GAME_FONT_SIZES)
from .game_board import GameBoard

class GameScreen:
    def __init__(self, screen: pygame.Surface, network_manager: Optional[Any] = None, loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        self._initialize_screen_properties(screen, network_manager, loop)
        self._calculate_board_dimensions()
        self._setup_game_boards()
        self._initialize_game_state()
        self._initialize_ship_tracking()
        self._setup_fonts()
        
    def _initialize_screen_properties(self, screen: pygame.Surface, network_manager: Optional[Any], loop: Optional[asyncio.AbstractEventLoop]) -> None:
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.network_manager = network_manager
        self.loop = loop or asyncio.get_event_loop()
        
    def _calculate_board_dimensions(self) -> None:
        available_height = self.height - GAME_TITLE_SPACE - GAME_BOARD_TITLE_SPACE - GAME_INFO_SPACE
        available_width = self.width - GAME_SCREEN_MARGIN
        
        max_board_width = (available_width - GAME_BOARD_SPACING) // GAME_SCREEN_DIVISION_FACTOR
        max_board_height = available_height
        
        self.board_size = int(min(max_board_width, max_board_height) * GAME_BOARD_SIZE_REDUCTION_FACTOR)
        self.start_x = self._calculate_board_start_x()
        self.board_y = self._calculate_board_y()
        
    def _calculate_board_start_x(self) -> int:
        total_width = self.board_size * GAME_SCREEN_DIVISION_FACTOR + GAME_BOARD_SPACING
        return (self.width - total_width) // GAME_SCREEN_DIVISION_FACTOR
        
    def _calculate_board_y(self) -> int:
        total_board_area = self.board_size + GAME_BOARD_TITLE_SPACE
        available_vertical = self.height - GAME_TITLE_SPACE - GAME_INFO_SPACE
        return GAME_TITLE_SPACE + (available_vertical - total_board_area) // GAME_SCREEN_DIVISION_FACTOR + GAME_BOARD_TITLE_SPACE
        
    def _setup_game_boards(self) -> None:
        self.my_board = GameBoard(self.start_x, self.board_y, self.board_size)
        enemy_board_x = self.start_x + self.board_size + GAME_BOARD_SPACING
        self.enemy_board = GameBoard(enemy_board_x, self.board_y, self.board_size)
        
    def _initialize_game_state(self) -> None:
        self.game_phase = GAME_PHASE_PLACEMENT
        self.selected_ship_size = DEFAULT_SHIP_SIZE
        self.ship_horizontal = SHIP_HORIZONTAL_DEFAULT
        self.my_turn = False
        self.ships_to_place = SHIP_SIZES.copy()
        self.current_ship_index = INITIAL_SHIP_INDEX
        
    def _initialize_ship_tracking(self) -> None:
        self.enemy_sunk_ships: List[str] = []
        self.enemy_sunk_ships_info: Dict[Tuple[int, int], str] = {}
        
    def _setup_fonts(self) -> None:
        self.font = pygame.font.Font(None, FONT_SIZE_NORMAL)
    
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_event(event)
        elif event.type == pygame.KEYDOWN:
            self._handle_keyboard_event(event)
            
    def _handle_mouse_event(self, event: pygame.event.Event) -> None:
        if event.button == MOUSE_LEFT_BUTTON:
            self.handle_left_click(event.pos)
        elif event.button == MOUSE_RIGHT_BUTTON:
            self.handle_right_click(event.pos)
            
    def _handle_keyboard_event(self, event: pygame.event.Event) -> None:
        if event.key == KEY_ROTATE:
            self.ship_horizontal = not self.ship_horizontal
    
    def handle_left_click(self, mouse_pos: Tuple[int, int]) -> None:
        if self._is_placement_phase():
            self._handle_ship_placement(mouse_pos)
        elif self._is_battle_phase_my_turn():
            self._handle_battle_shot(mouse_pos)
            
    def _is_placement_phase(self) -> bool:
        return (self.game_phase == GAME_PHASE_PLACEMENT and 
               self.current_ship_index < len(self.ships_to_place))
               
    def _is_battle_phase_my_turn(self) -> bool:
        return self.game_phase == GAME_PHASE_BATTLE and self.my_turn
        
    def _handle_ship_placement(self, mouse_pos: Tuple[int, int]) -> None:
        cell = self.my_board.get_cell_from_mouse(mouse_pos)
        if cell:
            ship_size = self.ships_to_place[self.current_ship_index]
            if self.my_board.place_ship(ship_size, cell[0], cell[1], self.ship_horizontal):
                self._advance_ship_placement()
                
    def _advance_ship_placement(self) -> None:
        self.current_ship_index += 1
        if self.current_ship_index >= len(self.ships_to_place):
            self.game_phase = GAME_PHASE_WAITING_BATTLE
            self.send_ships_to_server()
            
    def _handle_battle_shot(self, mouse_pos: Tuple[int, int]) -> None:
        try:
            cell = self.enemy_board.get_cell_from_mouse(mouse_pos)
            if self._can_shoot_at_cell(cell):
                if self.loop:
                    self.loop.create_task(self.network_manager.make_shot(cell[0], cell[1]))
                self.my_turn = False
        except Exception:
            pass
            
    def _can_shoot_at_cell(self, cell: Optional[Tuple[int, int]]) -> bool:
        return (cell is not None and 
               cell not in self.enemy_board.shots and 
               self.network_manager is not None)
    
    def handle_right_click(self, mouse_pos: Tuple[int, int]) -> None:
        self.ship_horizontal = not self.ship_horizontal
    
    def update(self) -> None:
        pass
    
    def draw(self) -> None:
        self.draw_ocean_background()
        self.draw_board_panels()
        self._draw_game_title()
        self._draw_board_titles()
        self._draw_game_boards()
        self._draw_ship_preview_if_needed()
        self._draw_game_info()
        
    def draw_without_preview(self) -> None:
        self.draw_ocean_background()
        self.draw_board_panels()
        self._draw_game_title()
        self._draw_board_titles()
        self._draw_game_boards()
        self._draw_game_info()
        
    def _draw_game_title(self) -> None:
        title_font = pygame.font.Font(None, GAME_FONT_SIZES['TITLE'])
        title_text = title_font.render(GAME_TEXT['TITLE'], True, COLOR_WHITE)
        title_rect = title_text.get_rect(center=(self.width // GAME_SCREEN_DIVISION_FACTOR, 35))
        self.screen.blit(title_text, title_rect)
        
    def _draw_board_titles(self) -> None:
        board_font = pygame.font.Font(None, GAME_FONT_SIZES['BOARD_TITLE'])
        title_y = self._calculate_board_title_y()
        
        self._draw_my_board_title(board_font, title_y)
        self._draw_enemy_board_title(board_font, title_y)
        
    def _calculate_board_title_y(self) -> int:
        panel_top = self.my_board.y - PANEL_PADDING - COORD_SPACE
        return panel_top - TITLE_SPACING
        
    def _draw_my_board_title(self, board_font: pygame.font.Font, title_y: int) -> None:
        my_title = board_font.render(GAME_TEXT['MY_FLEET'], True, SHIP_STATUS_COLORS['WHITE'])
        center_x = self.my_board.x + self.my_board.width // GAME_SCREEN_DIVISION_FACTOR
        my_title_rect = my_title.get_rect(center=(center_x, title_y))
        self.screen.blit(my_title, my_title_rect)
        
    def _draw_enemy_board_title(self, board_font: pygame.font.Font, title_y: int) -> None:
        enemy_title = board_font.render(GAME_TEXT['ENEMY'], True, SHIP_STATUS_COLORS['WHITE'])
        center_x = self.enemy_board.x + self.enemy_board.width // GAME_SCREEN_DIVISION_FACTOR
        enemy_title_rect = enemy_title.get_rect(center=(center_x, title_y))
        self.screen.blit(enemy_title, enemy_title_rect)
        
    def _draw_game_boards(self) -> None:
        self.my_board.draw(self.screen, show_ships=True)
        self.draw_enemy_board_with_sunk_ships()
        
        if self._should_show_ships_status():
            self.draw_ships_status()
            
    def _should_show_ships_status(self) -> bool:
        return (self.game_phase == GAME_PHASE_BATTLE or 
               self.game_phase == GAME_PHASE_WAITING_BATTLE)
               
    def _draw_ship_preview_if_needed(self) -> None:
        if self._should_show_ship_preview():
            mouse_pos = pygame.mouse.get_pos()
            cell = self.my_board.get_cell_from_mouse(mouse_pos)
            if cell:
                self.draw_ship_preview_realistic(cell[0], cell[1])
                
    def _should_show_ship_preview(self) -> bool:
        return (self.game_phase == GAME_PHASE_PLACEMENT and 
               self.current_ship_index < len(self.ships_to_place))
        
    def _draw_game_info(self) -> None:
        self.draw_info_panel()
        self._draw_status_text()
        self._draw_additional_info()
        
    def _draw_status_text(self) -> None:
        status_text = self._get_status_text()
        main_info_font = pygame.font.Font(None, GAME_FONT_SIZES['MAIN_INFO'])
        
        status_surface = main_info_font.render(status_text, True, SHIP_STATUS_COLORS['WHITE'])
        center_x = self.width // GAME_SCREEN_DIVISION_FACTOR
        status_rect = status_surface.get_rect(center=(center_x, self.height - 75))
        self.screen.blit(status_surface, status_rect)
        
    def _get_status_text(self) -> str:
        if self.game_phase == GAME_PHASE_PLACEMENT:
            return self._get_placement_status_text()
        elif self.game_phase == GAME_PHASE_BATTLE:
            return self._get_battle_status_text()
        elif self.game_phase == GAME_PHASE_WAITING_BATTLE:
            return GAME_TEXT['WAITING_BATTLE']
        else:
            return GAME_TEXT['PREPARING']
            
    def _get_placement_status_text(self) -> str:
        if self.current_ship_index < len(self.ships_to_place):
            ship_size = self.ships_to_place[self.current_ship_index]
            orientation = GAME_TEXT['HORIZONTAL'] if self.ship_horizontal else GAME_TEXT['VERTICAL']
            return GAME_TEXT['PLACING_SHIP'].format(ship_size, orientation)
        else:
            return GAME_TEXT['ALL_SHIPS_PLACED']
            
    def _get_battle_status_text(self) -> str:
        return GAME_TEXT['YOUR_TURN'] if self.my_turn else GAME_TEXT['OPPONENT_TURN']
            
    def _draw_additional_info(self) -> None:
        if self.game_phase == GAME_PHASE_PLACEMENT:
            remaining_ships = self.ships_to_place[self.current_ship_index:]
            if remaining_ships:
                self._draw_remaining_ships_info(remaining_ships)
                
    def _draw_remaining_ships_info(self, remaining_ships: List[int]) -> None:
        ships_text = GAME_TEXT['REMAINING_SHIPS'].format(remaining_ships)
        secondary_info_font = pygame.font.Font(None, GAME_FONT_SIZES['SECONDARY_INFO'])
        
        ships_surface = secondary_info_font.render(ships_text, True, SHIP_STATUS_COLORS['LIGHT_BLUE'])
        center_x = self.width // GAME_SCREEN_DIVISION_FACTOR
        ships_rect = ships_surface.get_rect(center=(center_x, self.height - 45))
        self.screen.blit(ships_surface, ships_rect)

    
    def draw_ocean_background(self) -> None:
        for y in range(self.height):
            ratio = y / self.height
            color = self._calculate_ocean_color(ratio)
            pygame.draw.line(self.screen, color, (0, y), (self.width, y))
            
    def _calculate_ocean_color(self, ratio: float) -> Tuple[int, int, int]:
        r = int(OCEAN_COLOR_TOP['r'] + (OCEAN_COLOR_BOTTOM['r'] - OCEAN_COLOR_TOP['r']) * ratio)
        g = int(OCEAN_COLOR_TOP['g'] + (OCEAN_COLOR_BOTTOM['g'] - OCEAN_COLOR_TOP['g']) * ratio)
        b = int(OCEAN_COLOR_TOP['b'] + (OCEAN_COLOR_BOTTOM['b'] - OCEAN_COLOR_TOP['b']) * ratio)
        return (r, g, b)
    
    def draw_board_panels(self) -> None:
        self._draw_my_board_panel()
        self._draw_enemy_board_panel()
        self._draw_panel_borders()
        
    def _draw_my_board_panel(self) -> None:
        my_panel_rect = self._calculate_my_panel_rect()
        my_panel_surface = self._create_panel_surface(my_panel_rect, MY_PANEL_COLOR)
        self.screen.blit(my_panel_surface, (my_panel_rect.x, my_panel_rect.y))
        
    def _draw_enemy_board_panel(self) -> None:
        enemy_panel_rect = self._calculate_enemy_panel_rect()
        enemy_panel_surface = self._create_panel_surface(enemy_panel_rect, ENEMY_PANEL_COLOR)
        self.screen.blit(enemy_panel_surface, (enemy_panel_rect.x, enemy_panel_rect.y))
        
    def _calculate_my_panel_rect(self) -> pygame.Rect:
        return pygame.Rect(
            self.my_board.x - PANEL_PADDING - COORD_SPACE,
            self.my_board.y - PANEL_PADDING - COORD_SPACE,
            self.my_board.width + PANEL_PADDING * 2 + COORD_SPACE * 2,
            self.my_board.height + PANEL_PADDING * 2 + COORD_SPACE * 2
        )
        
    def _calculate_enemy_panel_rect(self) -> pygame.Rect:
        return pygame.Rect(
            self.enemy_board.x - PANEL_PADDING - COORD_SPACE,
            self.enemy_board.y - PANEL_PADDING - COORD_SPACE,
            self.enemy_board.width + PANEL_PADDING * 2 + COORD_SPACE * 2,
            self.enemy_board.height + PANEL_PADDING * 2 + COORD_SPACE * 2
        )
        
    def _create_panel_surface(self, panel_rect: pygame.Rect, color: Tuple[int, int, int]) -> pygame.Surface:
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height))
        panel_surface.set_alpha(GAME_PANEL_ALPHA)
        panel_surface.fill(color)
        return panel_surface
        
    def _draw_panel_borders(self) -> None:
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
        ship_font = pygame.font.Font(None, 24)
        title_font = pygame.font.Font(None, 28)
        
        left_panel_x = 10
        left_panel_y = self.my_board.y + 50
        left_panel_width = 200
        left_panel_height = 300
        
        right_panel_x = self.width - 210
        right_panel_y = self.enemy_board.y + 50
        right_panel_width = 200
        right_panel_height = 300
        
        left_panel = pygame.Rect(left_panel_x, left_panel_y, left_panel_width, left_panel_height)
        left_surface = pygame.Surface((left_panel_width, left_panel_height))
        left_surface.set_alpha(180)
        left_surface.fill((20, 60, 40))
        self.screen.blit(left_surface, (left_panel_x, left_panel_y))
        pygame.draw.rect(self.screen, (100, 200, 120), left_panel, 2)
        
        my_title = title_font.render("MIS BARCOS", True, (255, 255, 255))
        self.screen.blit(my_title, (left_panel_x + 10, left_panel_y + 10))
        
        my_ships = self.my_board.get_ships_status()
        y_offset = 40
        for ship in my_ships:
            if ship['sunk']:
                color = (255, 100, 100)
                status = "HUNDIDO"
            else:
                color = (100, 255, 100)
                status = f"{ship['hits']}/{ship['total_hits_needed']} impactos"
            
            ship_text = ship_font.render(f"• {ship['name']}", True, color)
            status_text = ship_font.render(f"  {status}", True, (200, 200, 200))
            
            self.screen.blit(ship_text, (left_panel_x + 10, left_panel_y + y_offset))
            self.screen.blit(status_text, (left_panel_x + 15, left_panel_y + y_offset + 18))
            y_offset += 45
        
        right_panel = pygame.Rect(right_panel_x, right_panel_y, right_panel_width, right_panel_height)
        right_surface = pygame.Surface((right_panel_width, right_panel_height))
        right_surface.set_alpha(180)
        right_surface.fill((60, 20, 20))
        self.screen.blit(right_surface, (right_panel_x, right_panel_y))
        pygame.draw.rect(self.screen, (200, 100, 100), right_panel, 2)
        
        enemy_title = title_font.render("BARCOS ENEMIGOS", True, (255, 255, 255))
        self.screen.blit(enemy_title, (right_panel_x + 10, right_panel_y + 10))
        
        enemy_ships = self.get_enemy_ships_status()
        y_offset = 40
        for ship in enemy_ships:
            if ship['sunk']:
                color = (255, 100, 100)
                status = "HUNDIDO"
            else:
                color = (255, 200, 100)
                status = "ACTIVO"
            
            ship_text = ship_font.render(f" {ship['name']}", True, color)
            status_text = ship_font.render(f"  {status}", True, (200, 200, 200))
            
            self.screen.blit(ship_text, (right_panel_x + 10, right_panel_y + y_offset))
            self.screen.blit(status_text, (right_panel_x + 15, right_panel_y + y_offset + 18))
            y_offset += 45
    
    def get_enemy_ships_status(self):
        expected_ships = [
            {"name": "Portaaviones", "size": 5, "sunk": False},
            {"name": "Destructor Acorazado", "size": 4, "sunk": False},
            {"name": "Barco de Ataque #1", "size": 3, "sunk": False},
            {"name": "Barco de Ataque #2", "size": 3, "sunk": False},
            {"name": "Lancha Rapida", "size": 2, "sunk": False}
        ]
        
        for sunk_ship_name in self.enemy_sunk_ships:
            for ship in expected_ships:
                if ship['name'] == sunk_ship_name or (sunk_ship_name == "Barco de Ataque" and "Barco de Ataque" in ship['name'] and not ship['sunk']):
                    ship['sunk'] = True
                    break
        
        return expected_ships
    
    def draw_ship_preview_realistic(self, x, y):
        from .ship import Ship
        
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
        preview_surface.set_alpha(60)
        preview_surface.fill((0, 0, 0, 0))
        
        temp_board = GameBoard(self.my_board.x, self.my_board.y, self.my_board.width)
        temp_board.ships = [temp_ship]
        temp_board.colors = self.my_board.colors.copy()
        
        if can_place:
            temp_board.colors['ship'] = (0, 255, 0)
        else:
            temp_board.colors['ship'] = (255, 50, 50)
        
        temp_board.draw_realistic_ship(preview_surface, temp_ship)
        
        self.screen.blit(preview_surface, (0, 0))
    
    def send_ships_to_server(self):
        if self.network_manager:
            ships_data = []
            for ship in self.my_board.ships:
                ships_data.append(ship.positions)
            
            if self.loop:
                self.loop.create_task(self.network_manager.place_ships(ships_data))
    
    def handle_shot_result(self, data):
        if not data:
            return
            
        x, y = data.get('x'), data.get('y')
        result = data.get('result')
        shooter = data.get('shooter')
        ship_info = data.get('ship_info')
        
        if x is None or y is None or not result or not shooter:
            return
        
        sunk_ship_name = None
        if result == 'sunk' and ship_info:
            sunk_ship_name = ship_info.get('name')
            ship_size = ship_info.get('size')
            ship_positions = ship_info.get('positions', [])

        if result == 'hit' or result == 'sunk':
            self.play_missile_sound()
        elif result == 'miss':
            self.play_water_splash_sound()
        
        if shooter == self.network_manager.player_id:
            self.enemy_board.shots[(x, y)] = result
            
            if result == 'sunk' and sunk_ship_name and ship_info:
                self.enemy_sunk_ships.append(sunk_ship_name)

                ship_positions = ship_info.get('positions', [])
                for pos in ship_positions:
                    self.enemy_sunk_ships_info[tuple(pos)] = sunk_ship_name

                self.enemy_board.mark_enemy_ship_sunk(ship_info, ship_positions)
            
            if result == 'miss':
                self.my_turn = False
            
        else:
            self.my_board.shots[(x, y)] = result
            
            if result == 'hit' or result == 'sunk':
                for ship in self.my_board.ships:
                    if (x, y) in ship.positions:
                        ship.hit(x, y)
                        if ship.sunk and result == 'sunk':
                            pass
                        break
    
    def set_my_turn(self, is_my_turn):
        try:
            self.my_turn = bool(is_my_turn)
        except Exception:
            self.my_turn = False
    
    def start_battle_phase(self):
        self.game_phase = "battle"
    

    
    def draw_enemy_board_with_sunk_ships(self):
        self.enemy_board.draw(self.screen, show_ships=False)
    
    def play_missile_sound(self):
        try:
            missile_sound_path = os.path.join("assets", "sounds", "misil.mp3")
            if os.path.exists(missile_sound_path):
                missile_sound = pygame.mixer.Sound(missile_sound_path)
                missile_sound.set_volume(0.3)
                missile_sound.play()
        except (pygame.error, FileNotFoundError, Exception):
            pass
    
    def play_water_splash_sound(self):
        try:
            splash_sound_path = os.path.join("assets", "sounds", "waterSplash.mp3")
            if os.path.exists(splash_sound_path):
                splash_sound = pygame.mixer.Sound(splash_sound_path)
                splash_sound.set_volume(0.25)
                splash_sound.play()
        except (pygame.error, FileNotFoundError, Exception):
            pass

    def reset_game_state(self):
        self.my_board = GameBoard(self.my_board.x, self.my_board.y, self.my_board.width)
        self.enemy_board = GameBoard(self.enemy_board.x, self.enemy_board.y, self.enemy_board.width)

        self.game_phase = "placement"
        self.selected_ship_size = 2
        self.ship_horizontal = True
        self.my_turn = False
        self.ships_to_place = [5, 4, 3, 3, 2]
        self.current_ship_index = 0

        self.enemy_sunk_ships = []
        self.enemy_sunk_ships_info = {}