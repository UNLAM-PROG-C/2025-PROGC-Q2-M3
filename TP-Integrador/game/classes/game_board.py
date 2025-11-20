"""
Clase GameBoard para el cliente de Batalla Naval
Maneja el tablero de juego y la representación visual
"""
import pygame
import sys
import os

# Importar constants desde la carpeta padre del proyecto
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from constants import *

# Importar Ship desde el mismo paquete
from .ship import Ship


class GameBoard:
    """Tablero de juego para Batalla Naval."""
    
    def __init__(self, x, y, board_size=BOARD_SIZE_DEFAULT):
        """Inicializa el tablero de juego.
        
        Args:
            x: Posición X del tablero
            y: Posición Y del tablero
            board_size: Tamaño del tablero en píxeles
        """
        self.x = x
        self.y = y
        self.grid_size = GRID_SIZE
        self.width = board_size
        self.height = board_size
        self.cell_size = board_size // self.grid_size
        
        self._initialize_game_state()
        self._initialize_colors()
    
    def _initialize_game_state(self):
        """Inicializa el estado del juego."""
        self.grid = [['empty' for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.ships = []
        self.shots = {}
    
    def _initialize_colors(self):
        """Inicializa los colores utilizados en el tablero."""
        self.colors = {
            'water': COLOR_WATER,
            'ship': SHIP_HULL_COLOR,
            'hit': COLOR_HIT,
            'miss': COLOR_MISS,
            'grid': COLOR_GRID,
            'hover': COLOR_HOVER,
            'water_dark': COLOR_WATER_DARK,
        }
    
    def draw(self, screen, show_ships=True):
        """Dibuja el tablero completo."""
        self._draw_water_cells(screen)
        self._draw_grid_lines(screen)
        
        if show_ships:
            self._draw_all_ships(screen)
        
        self._draw_all_shots(screen)
        self.draw_coordinates(screen)
    
    def _draw_water_cells(self, screen):
        """Dibuja las celdas de agua con patrón alternado."""
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                cell_x = self.x + col * self.cell_size
                cell_y = self.y + row * self.cell_size
                
                if (row + col) % ALTERNATING_COLOR_MODULO == 0:
                    color = self.colors['water']
                else:
                    color = self.colors['water_dark']
                
                pygame.draw.rect(screen, color,
                               (cell_x, cell_y, self.cell_size, self.cell_size))
    
    def _draw_grid_lines(self, screen):
        """Dibuja las líneas de la grilla."""
        for i in range(self.grid_size + 1):
            line_width = GRID_LINE_WIDTH_THICK if i % GRID_LINE_INTERVAL == 0 else GRID_LINE_WIDTH_NORMAL
            
            # Líneas verticales
            pygame.draw.line(screen, self.colors['grid'], 
                           (self.x + i * self.cell_size, self.y),
                           (self.x + i * self.cell_size, self.y + self.height), line_width)
            # Líneas horizontales
            pygame.draw.line(screen, self.colors['grid'],
                           (self.x, self.y + i * self.cell_size),
                           (self.x + self.width, self.y + i * self.cell_size), line_width)
    
    def _draw_all_ships(self, screen):
        """Dibuja todos los barcos."""
        for ship in self.ships:
            self.draw_realistic_ship(screen, ship)
    
    def _draw_all_shots(self, screen):
        """Dibuja todos los disparos realizados."""
        for (shot_x, shot_y), result in self.shots.items():
            cell_x = self.x + shot_x * self.cell_size
            cell_y = self.y + shot_y * self.cell_size
            center_x = cell_x + self.cell_size // BOARD_DIVISION_FACTOR
            center_y = cell_y + self.cell_size // BOARD_DIVISION_FACTOR
            
            if result == 'hit' or result == 'sunk':
                self.draw_missile(screen, center_x, center_y, (220, 20, 60), 'hit')
            elif result == 'miss':
                self.draw_missile(screen, center_x, center_y, (255, 255, 255), 'miss')
    
    def draw_missile(self, screen, center_x, center_y, color, shot_type):
        """Dibuja un misil realista en la posición del disparo."""
        if shot_type == 'hit':
            self._draw_hit_missile(screen, center_x, center_y, color)
        else:  # miss
            self._draw_miss_missile(screen, center_x, center_y, color)
    
    def _draw_hit_missile(self, screen, center_x, center_y, color):
        """Dibuja misil de impacto con efectos de explosión."""
        self._draw_missile_body(screen, center_x, center_y, color)
        self._draw_missile_tip(screen, center_x, center_y, (180, 15, 45))
        self._draw_missile_fins(screen, center_x, center_y, (150, 10, 30))
        self._draw_explosion_effect(screen, center_x, center_y)
    
    def _draw_miss_missile(self, screen, center_x, center_y, color):
        """Dibuja misil de fallo con salpicadura de agua."""
        self._draw_missile_body(screen, center_x, center_y, color)
        self._draw_missile_tip(screen, center_x, center_y, (200, 200, 200))
        self._draw_missile_fins(screen, center_x, center_y, (180, 180, 180))
        self._draw_splash_effect(screen, center_x, center_y)
    
    def _draw_missile_body(self, screen, center_x, center_y, color):
        """Dibuja el cuerpo principal del misil."""
        missile_body = pygame.Rect(center_x - MISSILE_BODY_OFFSET_X, center_y - MISSILE_BODY_OFFSET_Y, 
                                 MISSILE_BODY_WIDTH, MISSILE_BODY_HEIGHT)
        pygame.draw.ellipse(screen, color, missile_body)
    
    def _draw_missile_tip(self, screen, center_x, center_y, tip_color):
        """Dibuja la punta del misil."""
        points = [
            (center_x, center_y - MISSILE_TIP_OFFSET),
            (center_x - MISSILE_TIP_WIDTH, center_y - MISSILE_TIP_HEIGHT),
            (center_x + MISSILE_TIP_WIDTH, center_y - MISSILE_TIP_HEIGHT)
        ]
        pygame.draw.polygon(screen, tip_color, points)
    
    def _draw_missile_fins(self, screen, center_x, center_y, fin_color):
        """Dibuja las aletas del misil."""
        # Aleta izquierda
        pygame.draw.polygon(screen, fin_color, [
            (center_x - MISSILE_BODY_OFFSET_X, center_y + MISSILE_TIP_HEIGHT),
            (center_x - MISSILE_FIN_OFFSET, center_y + MISSILE_FIN_OFFSET),
            (center_x - MISSILE_FIN_WIDTH, center_y + MISSILE_BODY_OFFSET_Y)
        ])
        # Aleta derecha
        pygame.draw.polygon(screen, fin_color, [
            (center_x + MISSILE_BODY_OFFSET_X, center_y + MISSILE_TIP_HEIGHT),
            (center_x + MISSILE_FIN_OFFSET, center_y + MISSILE_FIN_OFFSET),
            (center_x + MISSILE_FIN_WIDTH, center_y + MISSILE_BODY_OFFSET_Y)
        ])
    
    def _draw_explosion_effect(self, screen, center_x, center_y):
        """Dibuja efecto de explosión/fuego."""
        for i, explosion_color in enumerate(EXPLOSION_COLORS[:3]):
            explosion_radius = MISSILE_BODY_OFFSET_X - i * EXPLOSION_RADIUS_REDUCTION
            pygame.draw.circle(screen, explosion_color, 
                             (center_x, center_y + EXPLOSION_EFFECT_OFFSET), explosion_radius)
    
    def _draw_splash_effect(self, screen, center_x, center_y):
        """Dibuja efecto de salpicadura de agua."""
        for i, splash_color in enumerate(SPLASH_COLORS):
            splash_radius = SPLASH_EFFECT_RADIUS - i
            splash_y = center_y + SPLASH_EFFECT_Y_OFFSET + i * SPLASH_EFFECT_SPACING
            pygame.draw.circle(screen, splash_color, 
                             (center_x, splash_y), splash_radius)
    

    
    def draw_coordinates(self, screen):
        """Dibuja las coordenadas del tablero (A-J y 1-10)."""
        coord_font = self._get_coordinate_font()
        coord_bg_width, coord_bg_height = self._get_coordinate_background_size()
        
        self._draw_number_coordinates(screen, coord_font, coord_bg_width, coord_bg_height)
        self._draw_letter_coordinates(screen, coord_font, coord_bg_width, coord_bg_height)
    
    def _get_coordinate_font(self):
        """Obtiene la fuente para las coordenadas."""
        coord_font_size = max(MIN_COORD_FONT_SIZE, 
                            min(MAX_COORD_FONT_SIZE, self.cell_size // COORD_FONT_CELL_RATIO))
        return pygame.font.Font(None, coord_font_size)
    
    def _get_coordinate_background_size(self):
        """Calcula el tamaño del fondo de las coordenadas."""
        coord_bg_width = max(COORD_BG_MIN_WIDTH, self.cell_size // COORDINATE_BG_DIVISION_FACTOR)
        coord_bg_height = max(COORD_BG_MIN_HEIGHT, self.cell_size // COORDINATE_BG_HEIGHT_DIVISION)
        return coord_bg_width, coord_bg_height
    
    def _draw_number_coordinates(self, screen, coord_font, bg_width, bg_height):
        """Dibuja las coordenadas numéricas (1-10)."""
        for i in range(self.grid_size):
            num_text = coord_font.render(str(i + 1), True, COLOR_WHITE)
            
            bg_x = self.x - bg_width - COORD_BG_MARGIN
            bg_y = self.y + i * self.cell_size + (self.cell_size - bg_height) // BOARD_DIVISION_FACTOR
            num_bg = pygame.Rect(bg_x, bg_y, bg_width, bg_height)
            
            pygame.draw.rect(screen, COORDINATE_BG_COLOR, num_bg)
            pygame.draw.rect(screen, COLOR_WHITE, num_bg, COORDINATE_BORDER_WIDTH)
            
            text_rect = num_text.get_rect(center=num_bg.center)
            screen.blit(num_text, text_rect)
    
    def _draw_letter_coordinates(self, screen, coord_font, bg_width, bg_height):
        """Dibuja las coordenadas de letras (A-J)."""
        for i in range(self.grid_size):
            letter = chr(ord('A') + i)
            letter_text = coord_font.render(letter, True, COLOR_WHITE)
            
            bg_x = self.x + i * self.cell_size + (self.cell_size - bg_width) // BOARD_DIVISION_FACTOR
            bg_y = self.y - bg_height - COORD_BG_MARGIN
            letter_bg = pygame.Rect(bg_x, bg_y, bg_width, bg_height)
            
            pygame.draw.rect(screen, COORDINATE_BG_COLOR, letter_bg)
            pygame.draw.rect(screen, COLOR_WHITE, letter_bg, COORDINATE_BORDER_WIDTH)
            
            text_rect = letter_text.get_rect(center=letter_bg.center)
            screen.blit(letter_text, text_rect)
    
    def draw_realistic_ship(self, screen, ship):
        """Dibuja un barco realista en el tablero."""
        if not ship.positions:
            return
        
        ship_bounds = self._calculate_ship_bounds(ship)
        start_x, start_y, ship_width, ship_height = ship_bounds
        
        self._draw_ship_hull(screen, ship, start_x, start_y, ship_width, ship_height)
    
    def _calculate_ship_bounds(self, ship):
        """Calcula los límites del barco para el dibujo."""
        min_x = min(pos[0] for pos in ship.positions)
        max_x = max(pos[0] for pos in ship.positions)
        min_y = min(pos[1] for pos in ship.positions)
        max_y = max(pos[1] for pos in ship.positions)
        
        start_pixel_x = self.x + min_x * self.cell_size + CELL_MARGIN
        start_pixel_y = self.y + min_y * self.cell_size + CELL_MARGIN
        
        if ship.horizontal:
            ship_width = (max_x - min_x + 1) * self.cell_size - CELL_MARGIN_DOUBLE
            ship_height = self.cell_size - CELL_MARGIN_DOUBLE
        else:
            ship_width = self.cell_size - CELL_MARGIN_DOUBLE
            ship_height = (max_y - min_y + 1) * self.cell_size - CELL_MARGIN_DOUBLE
            
        return start_pixel_x, start_pixel_y, ship_width, ship_height
    
    def _draw_ship_hull(self, screen, ship, start_x, start_y, width, height):
        """Dibuja el casco principal del barco."""
        if ship.horizontal:
            self._draw_horizontal_ship_hull(screen, start_x, start_y, width, height)
        else:
            self._draw_vertical_ship_hull(screen, start_x, start_y, width, height)
            
        self.draw_ship_superstructure(screen, ship, start_x, start_y, width, height, ship.horizontal)
    
    def _draw_horizontal_ship_hull(self, screen, start_x, start_y, width, height):
        """Dibuja el casco de un barco horizontal."""
        # Casco principal con degradado
        hull_rect = pygame.Rect(start_x, start_y + SHIP_HULL_OFFSET, width, height - SHIP_HULL_HEIGHT_REDUCTION)
        pygame.draw.ellipse(screen, SHIP_HULL_COLOR, hull_rect)
        
        # Línea de agua
        water_line = pygame.Rect(start_x, start_y + hull_rect.height - SHIP_WATER_LINE_OFFSET, 
                                width, SHIP_WATER_LINE_HEIGHT)
        pygame.draw.ellipse(screen, SHIP_WATER_LINE_COLOR, water_line)
        
        # Cubierta principal
        deck_rect = pygame.Rect(start_x + SHIP_DECK_MARGIN, start_y + SHIP_DECK_OFFSET_Y, 
                               width - SHIP_DECK_WIDTH_REDUCTION, height - SHIP_DECK_HEIGHT_REDUCTION)
        pygame.draw.ellipse(screen, SHIP_DECK_COLOR, deck_rect)
    
    def _draw_vertical_ship_hull(self, screen, start_x, start_y, width, height):
        """Dibuja el casco de un barco vertical."""
        # Casco principal
        hull_rect = pygame.Rect(start_x + SHIP_HULL_OFFSET, start_y, width - SHIP_HULL_HEIGHT_REDUCTION, height)
        pygame.draw.ellipse(screen, SHIP_HULL_COLOR, hull_rect)
        
        # Línea de agua
        water_line = pygame.Rect(start_x + hull_rect.width - SHIP_WATER_LINE_OFFSET, start_y, 
                                SHIP_WATER_LINE_HEIGHT, height)
        pygame.draw.ellipse(screen, SHIP_WATER_LINE_COLOR, water_line)
        
        # Cubierta principal
        deck_rect = pygame.Rect(start_x + SHIP_DECK_OFFSET_Y, start_y + SHIP_DECK_MARGIN, 
                               width - SHIP_DECK_HEIGHT_REDUCTION, height - SHIP_DECK_WIDTH_REDUCTION)
        pygame.draw.ellipse(screen, SHIP_DECK_COLOR, deck_rect)
    
    def draw_ship_superstructure(self, screen, ship, start_x, start_y, width, height, horizontal):
        """Dibuja la superestructura específica según el tipo de barco."""
        if ship.size == SHIP_SIZE_CARRIER:  # Portaaviones
            self.draw_aircraft_carrier(screen, start_x, start_y, width, height, horizontal)
        elif ship.size == SHIP_SIZE_DESTROYER:  # Destructor
            self.draw_destroyer(screen, start_x, start_y, width, height, horizontal)
        elif ship.size == SHIP_SIZE_CRUISER:  # Barco de Ataque
            self.draw_attack_ship(screen, start_x, start_y, width, height, horizontal)
        elif ship.size == SHIP_SIZE_SUBMARINE:  # Lancha Táctica
            self.draw_tactical_boat(screen, start_x, start_y, width, height, horizontal)
    
    def draw_aircraft_carrier(self, screen, start_x, start_y, width, height, horizontal):
        """Dibuja portaaviones con cubierta de vuelo y torre de control."""
        if horizontal:
            self._draw_horizontal_aircraft_carrier(screen, start_x, start_y, width, height)
        else:
            self._draw_vertical_aircraft_carrier(screen, start_x, start_y, width, height)
    
    def _draw_horizontal_aircraft_carrier(self, screen, start_x, start_y, width, height):
        """Dibuja portaaviones horizontal."""
        # Cubierta de vuelo
        flight_deck = pygame.Rect(start_x + FLIGHT_DECK_MARGIN, start_y + FLIGHT_DECK_MARGIN, 
                                width - FLIGHT_DECK_WIDTH_REDUCTION, FLIGHT_DECK_HEIGHT)
        pygame.draw.rect(screen, FLIGHT_DECK_COLOR, flight_deck)
        
        # Torre de control (isla)
        tower_x = start_x + width * CARRIER_TOWER_X_RATIO
        tower = pygame.Rect(tower_x, start_y + FLIGHT_DECK_HEIGHT, CARRIER_TOWER_WIDTH, CARRIER_TOWER_HEIGHT)
        pygame.draw.rect(screen, TOWER_COLOR, tower)
        
        self._draw_carrier_details(screen, tower_x, start_x, start_y, width)
    
    def _draw_vertical_aircraft_carrier(self, screen, start_x, start_y, width, height):
        """Dibuja portaaviones vertical."""
        # Cubierta de vuelo vertical
        flight_deck = pygame.Rect(start_x + FLIGHT_DECK_MARGIN, start_y + FLIGHT_DECK_MARGIN, 
                                FLIGHT_DECK_HEIGHT, height - FLIGHT_DECK_WIDTH_REDUCTION)
        pygame.draw.rect(screen, FLIGHT_DECK_COLOR, flight_deck)
        
        # Torre de control vertical
        tower_y = start_y + height * CARRIER_TOWER_Y_RATIO
        tower = pygame.Rect(start_x + FLIGHT_DECK_HEIGHT, tower_y, CARRIER_TOWER_HEIGHT, CARRIER_TOWER_WIDTH)
        pygame.draw.rect(screen, TOWER_COLOR, tower)
    
    def _draw_carrier_details(self, screen, tower_x, start_x, start_y, width):
        """Dibuja detalles del portaaviones."""
        # Antenas de radar
        radar_x = tower_x + RADAR_OFFSET
        pygame.draw.line(screen, RADAR_ANTENNA_COLOR, 
                        (radar_x, start_y + FLIGHT_DECK_HEIGHT), 
                        (radar_x, start_y + RADAR_HEIGHT), RADAR_LINE_WIDTH)
        pygame.draw.circle(screen, RADAR_DISH_COLOR, (radar_x, start_y + RADAR_HEIGHT), RADAR_DISH_RADIUS)
        
        # Líneas de la cubierta
        for i in range(CARRIER_DECK_LINES):
            line_x = start_x + FLIGHT_DECK_MARGIN + i * (width - FLIGHT_DECK_WIDTH_REDUCTION) // CARRIER_DECK_LINES
            pygame.draw.line(screen, DECK_LINE_COLOR, 
                           (line_x, start_y + FLIGHT_DECK_LINE_Y1), 
                           (line_x, start_y + FLIGHT_DECK_LINE_Y2), DECK_LINE_WIDTH)
    
    def draw_destroyer(self, screen, start_x, start_y, width, height, horizontal):
        """Dibuja destructor con cañones y sistemas de defensa."""
        if horizontal:
            self._draw_horizontal_destroyer(screen, start_x, start_y, width, height)
        else:
            self._draw_vertical_destroyer(screen, start_x, start_y, width, height)
    
    def _draw_horizontal_destroyer(self, screen, start_x, start_y, width, height):
        """Dibuja destructor horizontal."""
        # Torreta principal delantera
        turret1_x = start_x + width * DESTROYER_TURRET1_RATIO
        pygame.draw.circle(screen, DESTROYER_TURRET_COLOR, 
                         (turret1_x, start_y + height // BOARD_DIVISION_FACTOR), DESTROYER_MAIN_TURRET_SIZE)
        
        # Cañón principal
        cannon_end_x = turret1_x + DESTROYER_MAIN_CANNON_LENGTH
        pygame.draw.line(screen, DESTROYER_CANNON_COLOR, 
                        (turret1_x, start_y + height // BOARD_DIVISION_FACTOR), 
                        (cannon_end_x, start_y + height // BOARD_DIVISION_FACTOR), DESTROYER_MAIN_CANNON_WIDTH)
        
        self._draw_destroyer_rear_turret(screen, start_x, start_y, width, height)
        self._draw_destroyer_bridge(screen, start_x, start_y, width, height)
    
    def _draw_destroyer_rear_turret(self, screen, start_x, start_y, width, height):
        """Dibuja la torreta trasera del destructor."""
        turret2_x = start_x + width * DESTROYER_TURRET2_RATIO
        pygame.draw.circle(screen, DESTROYER_TURRET_COLOR, 
                         (turret2_x, start_y + height // BOARD_DIVISION_FACTOR), DESTROYER_REAR_TURRET_SIZE)
        
        cannon_end_x2 = turret2_x - DESTROYER_REAR_CANNON_LENGTH
        pygame.draw.line(screen, DESTROYER_CANNON_COLOR, 
                        (turret2_x, start_y + height // BOARD_DIVISION_FACTOR), 
                        (cannon_end_x2, start_y + height // BOARD_DIVISION_FACTOR), DESTROYER_REAR_CANNON_WIDTH)
    
    def _draw_destroyer_bridge(self, screen, start_x, start_y, width, height):
        """Dibuja el puente de mando del destructor."""
        bridge_x = start_x + width * DESTROYER_BRIDGE_RATIO
        bridge = pygame.Rect(bridge_x - DESTROYER_BRIDGE_HALF_WIDTH, start_y + DESTROYER_BRIDGE_OFFSET, 
                           DESTROYER_BRIDGE_WIDTH, DESTROYER_BRIDGE_HEIGHT)
        pygame.draw.rect(screen, DESTROYER_BRIDGE_COLOR, bridge)
        
        # Ventanas del puente
        for i in range(DESTROYER_BRIDGE_WINDOWS):
            window_x = bridge_x - DESTROYER_WINDOW_OFFSET + i * DESTROYER_WINDOW_SPACING
            pygame.draw.rect(screen, DESTROYER_WINDOW_COLOR, 
                           (window_x, start_y + DESTROYER_WINDOW_Y, 
                            DESTROYER_WINDOW_WIDTH, DESTROYER_WINDOW_HEIGHT))
    
    def _draw_vertical_destroyer(self, screen, start_x, start_y, width, height):
        """Dibuja destructor vertical."""
        # Torreta principal
        turret1_y = start_y + height * DESTROYER_TURRET1_RATIO
        pygame.draw.circle(screen, DESTROYER_TURRET_COLOR, 
                         (start_x + width // BOARD_DIVISION_FACTOR, turret1_y), DESTROYER_MAIN_TURRET_SIZE)
        
        # Torreta trasera
        turret2_y = start_y + height * DESTROYER_TURRET2_RATIO
        pygame.draw.circle(screen, DESTROYER_TURRET_COLOR, 
                         (start_x + width // BOARD_DIVISION_FACTOR, turret2_y), DESTROYER_REAR_TURRET_SIZE)
    
    def draw_attack_ship(self, screen, start_x, start_y, width, height, horizontal):
        """Dibuja barco de ataque con misiles y cañones menores."""
        if horizontal:
            self._draw_horizontal_attack_ship(screen, start_x, start_y, width, height)
        else:
            self._draw_vertical_attack_ship(screen, start_x, start_y, width, height)
    
    def _draw_horizontal_attack_ship(self, screen, start_x, start_y, width, height):
        """Dibuja barco de ataque horizontal."""
        # Cañón principal
        gun_x = start_x + width * ATTACK_SHIP_GUN_RATIO
        pygame.draw.circle(screen, ATTACK_SHIP_GUN_COLOR, 
                         (gun_x, start_y + height // BOARD_DIVISION_FACTOR), ATTACK_SHIP_GUN_SIZE)
        pygame.draw.line(screen, ATTACK_SHIP_CANNON_COLOR, 
                        (gun_x, start_y + height // BOARD_DIVISION_FACTOR), 
                        (gun_x + ATTACK_SHIP_CANNON_LENGTH, start_y + height // BOARD_DIVISION_FACTOR), 
                        ATTACK_SHIP_CANNON_WIDTH)
        
        # Lanzamisiles y superestructura
        self._draw_attack_ship_missile_launcher(screen, start_x, start_y, width, height)
        self._draw_attack_ship_superstructure(screen, start_x, start_y, width, height)
    
    def _draw_vertical_attack_ship(self, screen, start_x, start_y, width, height):
        """Dibuja barco de ataque vertical."""
        # Cañón principal
        gun_y = start_y + height * ATTACK_SHIP_GUN_RATIO
        pygame.draw.circle(screen, ATTACK_SHIP_GUN_COLOR, 
                         (start_x + width // BOARD_DIVISION_FACTOR, gun_y), ATTACK_SHIP_GUN_SIZE)
        
        # Lanzamisiles
        missile_y = start_y + height * ATTACK_SHIP_MISSILE_RATIO
        missile_rect = pygame.Rect(start_x + width // BOARD_DIVISION_FACTOR - ATTACK_SHIP_MISSILE_HALF_WIDTH, 
                                 missile_y - ATTACK_SHIP_MISSILE_HALF_HEIGHT, 
                                 ATTACK_SHIP_MISSILE_WIDTH, ATTACK_SHIP_MISSILE_HEIGHT)
        pygame.draw.rect(screen, ATTACK_SHIP_MISSILE_COLOR, missile_rect)
    
    def _draw_attack_ship_missile_launcher(self, screen, start_x, start_y, width, height):
        """Dibuja el lanzamisiles del barco de ataque."""
        missile_x = start_x + width * ATTACK_SHIP_MISSILE_RATIO
        missile_rect = pygame.Rect(missile_x - ATTACK_SHIP_MISSILE_HALF_WIDTH, 
                                 start_y + height // BOARD_DIVISION_FACTOR - ATTACK_SHIP_MISSILE_HALF_HEIGHT, 
                                 ATTACK_SHIP_MISSILE_WIDTH, ATTACK_SHIP_MISSILE_HEIGHT)
        pygame.draw.rect(screen, ATTACK_SHIP_MISSILE_COLOR, missile_rect)
    
    def _draw_attack_ship_superstructure(self, screen, start_x, start_y, width, height):
        """Dibuja la superestructura del barco de ataque."""
        super_rect = pygame.Rect(start_x + width * ATTACK_SHIP_SUPERSTRUCTURE_RATIO, 
                               start_y + ATTACK_SHIP_MISSILE_HALF_HEIGHT, 
                               width * ATTACK_SHIP_CABIN_WIDTH_RATIO, 
                               ATTACK_SHIP_SUPERSTRUCTURE_HEIGHT)
        pygame.draw.rect(screen, ATTACK_SHIP_SUPERSTRUCTURE_COLOR, super_rect)
    
    def draw_tactical_boat(self, screen, start_x, start_y, width, height, horizontal):
        """Dibuja lancha táctica pequeña y ágil."""
        if horizontal:
            self._draw_horizontal_tactical_boat(screen, start_x, start_y, width, height)
        else:
            self._draw_vertical_tactical_boat(screen, start_x, start_y, width, height)
    
    def _draw_horizontal_tactical_boat(self, screen, start_x, start_y, width, height):
        """Dibuja lancha táctica horizontal."""
        # Cañón pequeño
        gun_x = start_x + width * TACTICAL_BOAT_GUN_RATIO
        pygame.draw.circle(screen, TACTICAL_BOAT_GUN_COLOR, 
                         (gun_x, start_y + height // BOARD_DIVISION_FACTOR), TACTICAL_BOAT_GUN_SIZE)
        pygame.draw.line(screen, TACTICAL_BOAT_CANNON_COLOR, 
                        (gun_x, start_y + height // BOARD_DIVISION_FACTOR), 
                        (gun_x + TACTICAL_BOAT_CANNON_LENGTH, start_y + height // BOARD_DIVISION_FACTOR), 
                        TACTICAL_BOAT_CANNON_WIDTH)
        
        self._draw_tactical_boat_cabin(screen, start_x, start_y, width, height)
    
    def _draw_tactical_boat_cabin(self, screen, start_x, start_y, width, height):
        """Dibuja la cabina de la lancha táctica."""
        # Cabina
        cabin = pygame.Rect(start_x + width * TACTICAL_BOAT_CABIN_RATIO, 
                          start_y + TACTICAL_BOAT_CABIN_OFFSET, 
                          width * TACTICAL_BOAT_CABIN_WIDTH_RATIO, 
                          TACTICAL_BOAT_CABIN_HEIGHT)
        pygame.draw.rect(screen, TACTICAL_BOAT_CABIN_COLOR, cabin)
        
        # Ventana
        window_x = start_x + width * TACTICAL_BOAT_WINDOW_OFFSET
        pygame.draw.rect(screen, TACTICAL_BOAT_WINDOW_COLOR, 
                       (window_x, start_y + TACTICAL_BOAT_WINDOW_Y_OFFSET, 
                        TACTICAL_BOAT_WINDOW_WIDTH, TACTICAL_BOAT_WINDOW_HEIGHT))
    
    def _draw_vertical_tactical_boat(self, screen, start_x, start_y, width, height):
        """Dibuja lancha táctica vertical."""
        # Cañón pequeño vertical
        gun_y = start_y + height * TACTICAL_BOAT_GUN_RATIO
        pygame.draw.circle(screen, TACTICAL_BOAT_GUN_COLOR, 
                         (start_x + width // BOARD_DIVISION_FACTOR, gun_y), TACTICAL_BOAT_GUN_SIZE)
        
        # Cabina vertical
        cabin = pygame.Rect(start_x + TACTICAL_BOAT_CABIN_OFFSET, 
                          start_y + height * TACTICAL_BOAT_CABIN_RATIO, 
                          TACTICAL_BOAT_CABIN_HEIGHT, 
                          height * TACTICAL_BOAT_CABIN_WIDTH_RATIO)
        pygame.draw.rect(screen, TACTICAL_BOAT_CABIN_COLOR, cabin)
    
    def get_cell_from_mouse(self, mouse_pos):
        """Obtiene las coordenadas de celda a partir de la posición del mouse."""
        mx, my = mouse_pos
        
        if not self._is_mouse_in_bounds(mx, my):
            return None
            
        return self._calculate_cell_from_position(mx, my)
    
    def _is_mouse_in_bounds(self, mx, my):
        """Verifica si el mouse está dentro de los límites del tablero."""
        return (self.x <= mx <= self.x + self.width and 
                self.y <= my <= self.y + self.height)
    
    def _calculate_cell_from_position(self, mx, my):
        """Calcula las coordenadas de celda basadas en la posición del mouse."""
        cell_x = (mx - self.x) // self.cell_size
        cell_y = (my - self.y) // self.cell_size
        
        if 0 <= cell_x < self.grid_size and 0 <= cell_y < self.grid_size:
            return (cell_x, cell_y)
        return None
    
    def can_place_ship(self, ship_size, start_x, start_y, horizontal=True):
        """Verifica si se puede colocar un barco en la posición especificada."""
        positions = self._generate_ship_positions(ship_size, start_x, start_y, horizontal)
        
        if not positions:
            return False
            
        return self._check_positions_available(positions)
    
    def _generate_ship_positions(self, ship_size, start_x, start_y, horizontal):
        """Genera las posiciones que ocuparía el barco."""
        positions = []
        
        for i in range(ship_size):
            if horizontal:
                x, y = start_x + i, start_y
            else:
                x, y = start_x, start_y + i
            
            if x >= self.grid_size or y >= self.grid_size:
                return None
            
            positions.append((x, y))
        return positions
    
    def _check_positions_available(self, positions):
        """Verifica si las posiciones están disponibles."""
        for x, y in positions:
            for ship in self.ships:
                if (x, y) in ship.positions:
                    return False
        return True
    
    def place_ship(self, ship_size, start_x, start_y, horizontal=True):
        """Coloca un barco en el tablero si es posible."""
        if not self.can_place_ship(ship_size, start_x, start_y, horizontal):
            return False
            
        ship = self._create_ship(ship_size, start_x, start_y, horizontal)
        self.ships.append(ship)
        return True
    
    def _create_ship(self, ship_size, start_x, start_y, horizontal):
        """Crea un nuevo barco con las posiciones especificadas."""
        ship = Ship(ship_size)
        ship.horizontal = horizontal
        
        for i in range(ship_size):
            if horizontal:
                x, y = start_x + i, start_y
            else:
                x, y = start_x, start_y + i
            ship.positions.append((x, y))
        
        return ship
    
    def get_ships_status(self):
        """Obtener el estado de todos los barcos"""
        ships_status = []
        for ship in self.ships:
            status = {
                'name': ship.name,
                'size': ship.size,
                'sunk': ship.sunk,
                'hits': len(ship.hits),
                'total_hits_needed': ship.size
            }
            ships_status.append(status)
        return ships_status
    
    def get_sunk_ship_name(self, x, y):
        """Obtener el nombre del barco hundido en la posición dada"""
        # Para barcos propios
        for ship in self.ships:
            if (x, y) in ship.positions and ship.sunk:
                return ship.name
        return None
    

    
    def mark_enemy_ship_sunk(self, ship_info, shot_positions):
        """Marcar un barco enemigo como hundido basándose en la información del servidor"""
        if not ship_info:
            return
        
        ship_name = ship_info.get('name')
        ship_size = ship_info.get('size') 
        ship_positions = ship_info.get('positions', [])
        
        # Marcar todas las posiciones del barco como 'sunk' en el tablero enemigo
        for pos_x, pos_y in ship_positions:
            self.shots[(pos_x, pos_y)] = 'sunk'
        
        print(f"🎯 Barco enemigo {ship_name} marcado como hundido en posiciones: {ship_positions}")