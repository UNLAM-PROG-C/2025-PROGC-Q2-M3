import pygame
import os

class Ship:
    def __init__(self, size):
        self.size = size
        self.positions = []
        self.hits = set()
        self.sunk = False
        self.horizontal = True
        
        # Asignar nombre según el tamaño
        if size == 5:
            self.name = "Portaaviones"
        elif size == 4:
            self.name = "Destructor Acorazado"
        elif size == 3:
            self.name = "Barco de Ataque"
        elif size == 2:
            self.name = "Lancha Rapida"
        else:
            self.name = f"Barco de {size} casillas"
    
    def is_sunk(self):
        return len(self.hits) >= self.size
    
    def hit(self, x, y):
        if (x, y) in self.positions:
            self.hits.add((x, y))
            if self.is_sunk():
                self.sunk = True
            return True
        return False

class GameBoard:
    def __init__(self, x, y, board_size=450):
        self.x = x
        self.y = y
        self.grid_size = 10
        self.width = board_size
        self.height = board_size
        self.cell_size = board_size // self.grid_size
        
        self.grid = [['empty' for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.ships = []
        self.shots = {}
        
        self.colors = {
            'water': (70, 130, 180),
            'ship': (101, 67, 33),
            'hit': (220, 20, 60),
            'miss': (255, 255, 255),
            'grid': (30, 60, 100),
            'hover': (255, 255, 0, 100),
            'water_dark': (50, 100, 150),
        }
    
    def draw(self, screen, show_ships=True):
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                cell_x = self.x + col * self.cell_size
                cell_y = self.y + row * self.cell_size
                
                if (row + col) % 2 == 0:
                    color = self.colors['water']
                else:
                    color = self.colors['water_dark']
                
                pygame.draw.rect(screen, color,
                               (cell_x, cell_y, self.cell_size, self.cell_size))
        
        for i in range(self.grid_size + 1):
            line_width = 2 if i % 5 == 0 else 1
            
            pygame.draw.line(screen, self.colors['grid'], 
                           (self.x + i * self.cell_size, self.y),
                           (self.x + i * self.cell_size, self.y + self.height), line_width)
            pygame.draw.line(screen, self.colors['grid'],
                           (self.x, self.y + i * self.cell_size),
                           (self.x + self.width, self.y + i * self.cell_size), line_width)

        if show_ships:
            for ship in self.ships:
                self.draw_realistic_ship(screen, ship)
        
        for (shot_x, shot_y), result in self.shots.items():
            cell_x = self.x + shot_x * self.cell_size
            cell_y = self.y + shot_y * self.cell_size
            center_x = cell_x + self.cell_size // 2
            center_y = cell_y + self.cell_size // 2
            
            if result == 'hit' or result == 'sunk':
                # Misil rojo para aciertos (hit o sunk)
                self.draw_missile(screen, center_x, center_y, (220, 20, 60), 'hit')
                
                # Si el barco está hundido, mostrar el nombre
                if result == 'sunk':
                    sunk_ship_name = self.get_sunk_ship_name(shot_x, shot_y)
                    if sunk_ship_name:
                        self.draw_sunk_ship_label(screen, center_x, center_y, sunk_ship_name)
            elif result == 'miss':
                # Misil blanco para fallos
                self.draw_missile(screen, center_x, center_y, (255, 255, 255), 'miss')
        
        # Dibujar coordenadas del tablero
        self.draw_coordinates(screen)
    
    def draw_missile(self, screen, center_x, center_y, color, shot_type):
        """Dibujar un misil realista en la posición del disparo"""
        if shot_type == 'hit':
            # Misil de impacto - más grande y con efectos de explosión
            missile_size = self.cell_size // 3
            
            # Cuerpo principal del misil (elipse vertical)
            missile_body = pygame.Rect(center_x - 8, center_y - 12, 16, 24)
            pygame.draw.ellipse(screen, color, missile_body)
            
            # Punta del misil
            points = [
                (center_x, center_y - 15),  # Punta superior
                (center_x - 6, center_y - 8),  # Izquierda
                (center_x + 6, center_y - 8)   # Derecha
            ]
            pygame.draw.polygon(screen, (180, 15, 45), points)
            
            # Aletas del misil
            pygame.draw.polygon(screen, (150, 10, 30), [
                (center_x - 8, center_y + 8),
                (center_x - 12, center_y + 15),
                (center_x - 4, center_y + 12)
            ])
            pygame.draw.polygon(screen, (150, 10, 30), [
                (center_x + 8, center_y + 8),
                (center_x + 12, center_y + 15),
                (center_x + 4, center_y + 12)
            ])
            
            # Efecto de explosión/fuego
            for i in range(3):
                explosion_color = [(255, 100, 0), (255, 150, 0), (255, 200, 0)][i]
                explosion_radius = 6 - i * 2
                pygame.draw.circle(screen, explosion_color, 
                                 (center_x, center_y + 5), explosion_radius)
            
        else:  # miss
            # Misil de fallo - más pequeño, blanco/gris
            missile_size = self.cell_size // 4
            
            # Cuerpo principal del misil
            missile_body = pygame.Rect(center_x - 6, center_y - 10, 12, 20)
            pygame.draw.ellipse(screen, color, missile_body)
            
            # Punta del misil
            points = [
                (center_x, center_y - 12),  # Punta superior
                (center_x - 4, center_y - 6),  # Izquierda
                (center_x + 4, center_y - 6)   # Derecha
            ]
            pygame.draw.polygon(screen, (200, 200, 200), points)
            
            # Aletas del misil
            pygame.draw.polygon(screen, (180, 180, 180), [
                (center_x - 6, center_y + 6),
                (center_x - 9, center_y + 12),
                (center_x - 3, center_y + 10)
            ])
            pygame.draw.polygon(screen, (180, 180, 180), [
                (center_x + 6, center_y + 6),
                (center_x + 9, center_y + 12),
                (center_x + 3, center_y + 10)
            ])
            
            # Salpicadura de agua (círculos azules)
            splash_colors = [(100, 150, 255), (150, 200, 255), (200, 230, 255)]
            for i, splash_color in enumerate(splash_colors):
                splash_radius = 4 - i
                splash_y = center_y + 8 + i * 2
                pygame.draw.circle(screen, splash_color, 
                                 (center_x, splash_y), splash_radius)
    
    def draw_sunk_ship_label(self, screen, center_x, center_y, ship_name):
        """Dibujar etiqueta del barco hundido"""
        label_font = pygame.font.Font(None, 20)
        
        # Crear texto
        text_surface = label_font.render(ship_name, True, (255, 255, 0))
        text_rect = text_surface.get_rect()
        
        # Posicionar el texto arriba del misil
        label_x = center_x - text_rect.width // 2
        label_y = center_y - 35
        
        # Fondo semi-transparente para el texto
        bg_rect = pygame.Rect(label_x - 3, label_y - 2, text_rect.width + 6, text_rect.height + 4)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(180)
        bg_surface.fill((0, 0, 0))
        
        screen.blit(bg_surface, (bg_rect.x, bg_rect.y))
        pygame.draw.rect(screen, (255, 255, 0), bg_rect, 1)
        screen.blit(text_surface, (label_x, label_y))
    
    def draw_coordinates(self, screen):
        """Dibujar las coordenadas del tablero"""
        coord_font_size = max(20, min(32, self.cell_size // 2))
        coord_font = pygame.font.Font(None, coord_font_size)
        coord_bg_width = max(25, self.cell_size // 3)
        coord_bg_height = max(20, self.cell_size // 4)
        
        for i in range(self.grid_size):
            # Números a la izquierda
            num_text = coord_font.render(str(i + 1), True, (255, 255, 255))
            num_bg = pygame.Rect(self.x - coord_bg_width - 8, self.y + i * self.cell_size + (self.cell_size - coord_bg_height) // 2, coord_bg_width, coord_bg_height)
            pygame.draw.rect(screen, (50, 80, 120), num_bg)
            pygame.draw.rect(screen, (255, 255, 255), num_bg, 1)
            text_rect = num_text.get_rect(center=num_bg.center)
            screen.blit(num_text, text_rect)
            
            # Letras arriba
            letter = chr(ord('A') + i)
            letter_text = coord_font.render(letter, True, (255, 255, 255))
            letter_bg = pygame.Rect(self.x + i * self.cell_size + (self.cell_size - coord_bg_width) // 2, self.y - coord_bg_height - 8, coord_bg_width, coord_bg_height)
            pygame.draw.rect(screen, (50, 80, 120), letter_bg)
            pygame.draw.rect(screen, (255, 255, 255), letter_bg, 1)
            text_rect = letter_text.get_rect(center=letter_bg.center)
            screen.blit(letter_text, text_rect)
    
    def draw_realistic_ship(self, screen, ship):
        if not ship.positions:
            return
        
        # Colores base más realistas
        hull_color = (45, 55, 65)  # Gris azulado oscuro
        deck_color = (120, 100, 80)  # Madera
        metal_color = (85, 85, 85)  # Metal
        cannon_color = (40, 40, 40)  # Negro metálico
        detail_color = (200, 180, 140)  # Detalles dorados
        window_color = (100, 150, 200)  # Ventanas azules
        hit_color = (255, 0, 0)
        
        margin = 2
        
        min_x = min(pos[0] for pos in ship.positions)
        max_x = max(pos[0] for pos in ship.positions)
        min_y = min(pos[1] for pos in ship.positions)
        max_y = max(pos[1] for pos in ship.positions)
        
        start_pixel_x = self.x + min_x * self.cell_size + margin
        start_pixel_y = self.y + min_y * self.cell_size + margin
        
        if ship.horizontal:
            ship_width = (max_x - min_x + 1) * self.cell_size - 2 * margin
            ship_height = self.cell_size - 2 * margin
            
            # Casco principal con degradado
            hull_rect = pygame.Rect(start_pixel_x, start_pixel_y + 6, ship_width, ship_height - 12)
            pygame.draw.ellipse(screen, hull_color, hull_rect)
            
            # Línea de agua (más clara)
            water_line = pygame.Rect(start_pixel_x, start_pixel_y + hull_rect.height - 4, ship_width, 8)
            pygame.draw.ellipse(screen, (65, 75, 85), water_line)
            
            # Cubierta principal
            deck_rect = pygame.Rect(start_pixel_x + 4, start_pixel_y + 8, ship_width - 8, ship_height - 20)
            pygame.draw.ellipse(screen, deck_color, deck_rect)
            
            # Superestructura según el tamaño del barco
            self.draw_ship_superstructure(screen, ship, start_pixel_x, start_pixel_y, ship_width, ship_height, True)
            
        else:  # Vertical
            ship_width = self.cell_size - 2 * margin
            ship_height = (max_y - min_y + 1) * self.cell_size - 2 * margin
            
            # Casco principal
            hull_rect = pygame.Rect(start_pixel_x + 6, start_pixel_y, ship_width - 12, ship_height)
            pygame.draw.ellipse(screen, hull_color, hull_rect)
            
            # Línea de agua
            water_line = pygame.Rect(start_pixel_x + hull_rect.width - 4, start_pixel_y, 8, ship_height)
            pygame.draw.ellipse(screen, (65, 75, 85), water_line)
            
            # Cubierta principal
            deck_rect = pygame.Rect(start_pixel_x + 8, start_pixel_y + 4, ship_width - 20, ship_height - 8)
            pygame.draw.ellipse(screen, deck_color, deck_rect)
            
            # Superestructura según el tamaño del barco
            self.draw_ship_superstructure(screen, ship, start_pixel_x, start_pixel_y, ship_width, ship_height, False)
        
        # Dibujar impactos de balas si los hay
        for pos_x, pos_y in ship.positions:
            if (pos_x, pos_y) in ship.hits:
                hit_x = self.x + pos_x * self.cell_size + self.cell_size // 2
                hit_y = self.y + pos_y * self.cell_size + self.cell_size // 2
                
                # Efecto de explosión más dramático
                pygame.draw.circle(screen, (255, 0, 0), (hit_x, hit_y), 12)
                pygame.draw.circle(screen, (255, 100, 0), (hit_x, hit_y), 8)
                pygame.draw.circle(screen, (255, 200, 0), (hit_x, hit_y), 5)
                pygame.draw.circle(screen, (255, 255, 100), (hit_x, hit_y), 3)
    
    def draw_ship_superstructure(self, screen, ship, start_x, start_y, width, height, horizontal):
        """Dibujar la superestructura específica según el tipo de barco"""
        # Colores para detalles
        metal_color = (85, 85, 85)
        cannon_color = (40, 40, 40)
        detail_color = (200, 180, 140)
        window_color = (100, 150, 200)
        radar_color = (60, 60, 60)
        
        if ship.size == 5:  # Portaaviones
            self.draw_aircraft_carrier(screen, start_x, start_y, width, height, horizontal)
        elif ship.size == 4:  # Destructor
            self.draw_destroyer(screen, start_x, start_y, width, height, horizontal)
        elif ship.size == 3:  # Barco de Ataque
            self.draw_attack_ship(screen, start_x, start_y, width, height, horizontal)
        elif ship.size == 2:  # Lancha Táctica
            self.draw_tactical_boat(screen, start_x, start_y, width, height, horizontal)
    
    def draw_aircraft_carrier(self, screen, start_x, start_y, width, height, horizontal):
        """Dibujar portaaviones con cubierta de vuelo y torre de control"""
        if horizontal:
            # Cubierta de vuelo
            flight_deck = pygame.Rect(start_x + 5, start_y + 5, width - 10, 8)
            pygame.draw.rect(screen, (90, 90, 90), flight_deck)
            
            # Torre de control (isla)
            tower_x = start_x + width * 0.7
            tower = pygame.Rect(tower_x, start_y + 8, 15, 20)
            pygame.draw.rect(screen, (70, 70, 70), tower)
            
            # Antenas de radar
            pygame.draw.line(screen, (200, 200, 200), (tower_x + 7, start_y + 8), (tower_x + 7, start_y + 3), 2)
            pygame.draw.circle(screen, (100, 255, 100), (tower_x + 7, start_y + 3), 3)
            
            # Líneas de la cubierta
            for i in range(3):
                line_x = start_x + 10 + i * (width - 20) // 3
                pygame.draw.line(screen, (70, 70, 70), (line_x, start_y + 6), (line_x, start_y + 12), 1)
        else:
            # Versión vertical del portaaviones
            flight_deck = pygame.Rect(start_x + 5, start_y + 5, 8, height - 10)
            pygame.draw.rect(screen, (90, 90, 90), flight_deck)
            
            tower_y = start_y + height * 0.3
            tower = pygame.Rect(start_x + 8, tower_y, 20, 15)
            pygame.draw.rect(screen, (70, 70, 70), tower)
    
    def draw_destroyer(self, screen, start_x, start_y, width, height, horizontal):
        """Dibujar destructor con cañones y sistemas de defensa"""
        if horizontal:
            # Torreta principal delantera
            turret1_x = start_x + width * 0.2
            pygame.draw.circle(screen, (60, 60, 60), (turret1_x, start_y + height // 2), 8)
            # Cañón principal
            cannon_end_x = turret1_x + 15
            pygame.draw.line(screen, (40, 40, 40), (turret1_x, start_y + height // 2), 
                           (cannon_end_x, start_y + height // 2), 4)
            
            # Torreta trasera
            turret2_x = start_x + width * 0.8
            pygame.draw.circle(screen, (60, 60, 60), (turret2_x, start_y + height // 2), 6)
            cannon_end_x2 = turret2_x - 12
            pygame.draw.line(screen, (40, 40, 40), (turret2_x, start_y + height // 2), 
                           (cannon_end_x2, start_y + height // 2), 3)
            
            # Puente de mando
            bridge_x = start_x + width * 0.5
            bridge = pygame.Rect(bridge_x - 8, start_y + 8, 16, 12)
            pygame.draw.rect(screen, (80, 80, 80), bridge)
            
            # Ventanas del puente
            for i in range(3):
                window_x = bridge_x - 6 + i * 4
                pygame.draw.rect(screen, (100, 150, 200), (window_x, start_y + 10, 2, 3))
        else:
            # Versión vertical
            turret1_y = start_y + height * 0.2
            pygame.draw.circle(screen, (60, 60, 60), (start_x + width // 2, turret1_y), 8)
            
            turret2_y = start_y + height * 0.8
            pygame.draw.circle(screen, (60, 60, 60), (start_x + width // 2, turret2_y), 6)
    
    def draw_attack_ship(self, screen, start_x, start_y, width, height, horizontal):
        """Dibujar barco de ataque con misiles y cañones menores"""
        if horizontal:
            # Cañón principal
            gun_x = start_x + width * 0.3
            pygame.draw.circle(screen, (50, 50, 50), (gun_x, start_y + height // 2), 6)
            pygame.draw.line(screen, (35, 35, 35), (gun_x, start_y + height // 2), 
                           (gun_x + 10, start_y + height // 2), 3)
            
            # Lanzamisiles
            missile_x = start_x + width * 0.7
            missile_rect = pygame.Rect(missile_x - 4, start_y + height // 2 - 3, 8, 6)
            pygame.draw.rect(screen, (70, 70, 70), missile_rect)
            
            # Superestructura
            super_rect = pygame.Rect(start_x + width * 0.4, start_y + 6, width * 0.3, 14)
            pygame.draw.rect(screen, (75, 75, 75), super_rect)
        else:
            # Versión vertical
            gun_y = start_y + height * 0.3
            pygame.draw.circle(screen, (50, 50, 50), (start_x + width // 2, gun_y), 6)
            
            missile_y = start_y + height * 0.7
            missile_rect = pygame.Rect(start_x + width // 2 - 3, missile_y - 4, 6, 8)
            pygame.draw.rect(screen, (70, 70, 70), missile_rect)
    
    def draw_tactical_boat(self, screen, start_x, start_y, width, height, horizontal):
        """Dibujar lancha táctica pequeña y ágil"""
        if horizontal:
            # Cañón pequeño
            gun_x = start_x + width * 0.4
            pygame.draw.circle(screen, (45, 45, 45), (gun_x, start_y + height // 2), 4)
            pygame.draw.line(screen, (30, 30, 30), (gun_x, start_y + height // 2), 
                           (gun_x + 8, start_y + height // 2), 2)
            
            # Cabina
            cabin = pygame.Rect(start_x + width * 0.6, start_y + 8, width * 0.3, 10)
            pygame.draw.rect(screen, (70, 70, 70), cabin)
            
            # Ventana
            pygame.draw.rect(screen, (100, 150, 200), (start_x + width * 0.65, start_y + 10, 4, 3))
        else:
            # Versión vertical
            gun_y = start_y + height * 0.4
            pygame.draw.circle(screen, (45, 45, 45), (start_x + width // 2, gun_y), 4)
            
            cabin = pygame.Rect(start_x + 8, start_y + height * 0.6, 10, height * 0.3)
            pygame.draw.rect(screen, (70, 70, 70), cabin)
    
    def get_cell_from_mouse(self, mouse_pos):
        mx, my = mouse_pos
        if (self.x <= mx <= self.x + self.width and 
            self.y <= my <= self.y + self.height):
            cell_x = (mx - self.x) // self.cell_size
            cell_y = (my - self.y) // self.cell_size
            if 0 <= cell_x < self.grid_size and 0 <= cell_y < self.grid_size:
                return (cell_x, cell_y)
        return None
    
    def can_place_ship(self, ship_size, start_x, start_y, horizontal=True):
        positions = []
        
        for i in range(ship_size):
            if horizontal:
                x, y = start_x + i, start_y
            else:
                x, y = start_x, start_y + i
            
            if x >= self.grid_size or y >= self.grid_size:
                return False
            
            for ship in self.ships:
                if (x, y) in ship.positions:
                    return False
            
            positions.append((x, y))
        
        return True
    
    def place_ship(self, ship_size, start_x, start_y, horizontal=True):
        if self.can_place_ship(ship_size, start_x, start_y, horizontal):
            ship = Ship(ship_size)
            ship.horizontal = horizontal
            
            for i in range(ship_size):
                if horizontal:
                    x, y = start_x + i, start_y
                else:
                    x, y = start_x, start_y + i
                ship.positions.append((x, y))
            
            self.ships.append(ship)
            return True
        return False
    
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
        for ship in self.ships:
            if (x, y) in ship.positions and ship.sunk:
                return ship.name
        return None

class GameScreen:
    def __init__(self, screen, network_manager=None):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.network_manager = network_manager
        
        # Calcular tamaño para los tableros
        title_space = 80   # Espacio para título principal arriba
        board_title_space = 60  # Más espacio para títulos fuera de paneles
        info_space = 150   # Espacio para información abajo
        available_height = self.height - title_space - board_title_space - info_space
        available_width = self.width - 160  # Más margen para coordenadas
        
        # Separar mucho más los tableros para que no se toquen
        board_spacing = 150  # Separación mucho mayor
        max_board_width = (available_width - board_spacing) // 2
        max_board_height = available_height
        
        # Reducir el tamaño un 20% para dar más espacio de separación
        board_size = int(min(max_board_width, max_board_height) * 0.8)
        
        # Centrar los tableros horizontalmente y verticalmente
        total_width = board_size * 2 + board_spacing
        start_x = (self.width - total_width) // 2
        
        # Centrar verticalmente considerando todos los espacios
        total_board_area = board_size + board_title_space  # Tablero + espacio para su título
        available_vertical = self.height - title_space - info_space
        board_y = title_space + (available_vertical - total_board_area) // 2 + board_title_space
        
        self.my_board = GameBoard(start_x, board_y, board_size)
        self.enemy_board = GameBoard(start_x + board_size + board_spacing, board_y, board_size)
        
        self.game_phase = "placement"
        self.selected_ship_size = 2
        self.ship_horizontal = True
        self.my_turn = False
        
        self.ships_to_place = [5, 4, 3, 3, 2]
        self.current_ship_index = 0
        
        # Seguimiento de barcos enemigos hundidos
        self.enemy_sunk_ships = []
        
        self.font = pygame.font.Font(None, 32)
        
        print("✅ Sistema de barcos realistas inicializado")
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.handle_left_click(event.pos)
            elif event.button == 3:
                self.handle_right_click(event.pos)
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.ship_horizontal = not self.ship_horizontal
    
    def handle_left_click(self, mouse_pos):
        if self.game_phase == "placement":
            cell = self.my_board.get_cell_from_mouse(mouse_pos)
            if cell and self.current_ship_index < len(self.ships_to_place):
                ship_size = self.ships_to_place[self.current_ship_index]
                
                if self.my_board.place_ship(ship_size, cell[0], cell[1], self.ship_horizontal):
                    self.current_ship_index += 1
                    if self.current_ship_index >= len(self.ships_to_place):
                        self.game_phase = "waiting_for_battle"
                        self.send_ships_to_server()
        
        elif self.game_phase == "battle":
            if self.my_turn:
                cell = self.enemy_board.get_cell_from_mouse(mouse_pos)
                if cell and cell not in self.enemy_board.shots:
                    if self.network_manager:
                        self.network_manager.make_shot(cell[0], cell[1])
                        # No cambiar el turno aquí - esperar respuesta del servidor
    
    def handle_right_click(self, mouse_pos):
        self.ship_horizontal = not self.ship_horizontal
    
    def update(self):
        pass
    
    def draw(self):
        self.draw_ocean_background()
        
        self.draw_board_panels()
        
        title_font = pygame.font.Font(None, 56)
        title_text = title_font.render("BATALLA NAVAL", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.width // 2, 35))
        self.screen.blit(title_text, title_rect)
        
        board_font = pygame.font.Font(None, 42)
        
        # Posicionar títulos fuera del recuadro, con espacio de separación
        title_spacing = 15  # Espacio entre título y panel del tablero
        
        my_title = board_font.render("MI FLOTA", True, (255, 255, 255))
        my_panel_top = self.my_board.y - 40 - 15  # panel_padding + coord_space desde draw_board_panels
        my_title_rect = my_title.get_rect(center=(self.my_board.x + self.my_board.width // 2, my_panel_top - title_spacing))
        self.screen.blit(my_title, my_title_rect)
        
        enemy_title = board_font.render("ENEMIGO", True, (255, 255, 255))
        enemy_panel_top = self.enemy_board.y - 40 - 15  # panel_padding + coord_space desde draw_board_panels
        enemy_title_rect = enemy_title.get_rect(center=(self.enemy_board.x + self.enemy_board.width // 2, enemy_panel_top - title_spacing))
        self.screen.blit(enemy_title, enemy_title_rect)
        
        self.my_board.draw(self.screen, show_ships=True)
        self.enemy_board.draw(self.screen, show_ships=False)
        
        # Dibujar estado de los barcos si estamos en batalla
        if self.game_phase == "battle" or self.game_phase == "waiting_for_battle":
            self.draw_ships_status()
        
        if self.game_phase == "placement" and self.current_ship_index < len(self.ships_to_place):
            mouse_pos = pygame.mouse.get_pos()
            cell = self.my_board.get_cell_from_mouse(mouse_pos)
            if cell:
                self.draw_ship_preview_realistic(cell[0], cell[1])
        
        self.draw_info_panel()
        
        # Fuentes más grandes para mejor legibilidad
        main_info_font = pygame.font.Font(None, 32)
        secondary_info_font = pygame.font.Font(None, 28)
        
        if self.game_phase == "placement":
            if self.current_ship_index < len(self.ships_to_place):
                ship_size = self.ships_to_place[self.current_ship_index]
                orientation = "Horizontal" if self.ship_horizontal else "Vertical"
                status_text = f"Colocando barco de tamaño {ship_size} ({orientation}) - Click derecho o R para rotar"
            else:
                status_text = "Todos los barcos colocados - Esperando al oponente..."
        elif self.game_phase == "battle":
            if self.my_turn:
                status_text = "¡Tu turno! Haz click en el tablero enemigo para disparar"
            else:
                status_text = "Turno del oponente - Espera tu turno..."
        elif self.game_phase == "waiting_for_battle":
            status_text = "Barcos colocados - Esperando que inicie la batalla..."
        else:
            status_text = "Preparando juego..."
        
        # Texto principal centrado en el panel
        status_surface = main_info_font.render(status_text, True, (255, 255, 255))
        status_rect = status_surface.get_rect(center=(self.width // 2, self.height - 75))
        self.screen.blit(status_surface, status_rect)
        
        # Información adicional
        if self.game_phase == "placement":
            remaining_ships = self.ships_to_place[self.current_ship_index:]
            if remaining_ships:
                ships_text = f"Barcos restantes: {remaining_ships}"
                ships_surface = secondary_info_font.render(ships_text, True, (200, 220, 255))
                ships_rect = ships_surface.get_rect(center=(self.width // 2, self.height - 45))
                self.screen.blit(ships_surface, ships_rect)
        

    
    def draw_ocean_background(self):
        for y in range(self.height):
            ratio = y / self.height
            r = int(30 + (70 - 30) * ratio)
            g = int(60 + (130 - 60) * ratio)  
            b = int(90 + (200 - 90) * ratio)
            color = (r, g, b)
            pygame.draw.line(self.screen, color, (0, y), (self.width, y))
    
    def draw_board_panels(self):
        panel_padding = 15
        panel_color = (0, 0, 0, 100)
        border_color = (255, 255, 255, 150)
        
        coord_space = 40  # Espacio para las coordenadas
        
        my_panel = pygame.Rect(
            self.my_board.x - panel_padding - coord_space,
            self.my_board.y - panel_padding - coord_space,
            self.my_board.width + panel_padding * 2 + coord_space * 2,
            self.my_board.height + panel_padding * 2 + coord_space * 2
        )
        
        enemy_panel = pygame.Rect(
            self.enemy_board.x - panel_padding - coord_space,
            self.enemy_board.y - panel_padding - coord_space,
            self.enemy_board.width + panel_padding * 2 + coord_space * 2,
            self.enemy_board.height + panel_padding * 2 + coord_space * 2
        )
        
        my_panel_surface = pygame.Surface((my_panel.width, my_panel.height))
        my_panel_surface.set_alpha(100)
        my_panel_surface.fill((20, 40, 60))
        
        enemy_panel_surface = pygame.Surface((enemy_panel.width, enemy_panel.height))
        enemy_panel_surface.set_alpha(100)
        enemy_panel_surface.fill((40, 20, 20))
        
        self.screen.blit(my_panel_surface, (my_panel.x, my_panel.y))
        self.screen.blit(enemy_panel_surface, (enemy_panel.x, enemy_panel.y))
        
        pygame.draw.rect(self.screen, (100, 149, 237), my_panel, 3)
        pygame.draw.rect(self.screen, (220, 20, 60), enemy_panel, 3)
    
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
        sunk_ship_name = data.get('sunk_ship_name')  # Nombre del barco hundido (si aplica)
        
        if shooter == self.network_manager.player_id:
            # Mi disparo - registrar en el tablero enemigo
            self.enemy_board.shots[(x, y)] = result
            
            # Si hundí un barco enemigo, agregarlo a la lista
            if result == 'sunk' and sunk_ship_name:
                if sunk_ship_name not in self.enemy_sunk_ships:
                    self.enemy_sunk_ships.append(sunk_ship_name)
                    print(f"¡Hundiste el {sunk_ship_name} enemigo!")
            
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
                        if ship.sunk:
                            print(f"¡El enemigo hundió tu {ship.name}!")
                        break
    
    def set_my_turn(self, is_my_turn):
        self.my_turn = is_my_turn
    
    def start_battle_phase(self):
        print("🚀 Iniciando fase de batalla...")
        self.game_phase = "battle"
