import pygame

class Ship:
    def __init__(self, size):
        self.size = size
        self.positions = []
        self.hits = set()
        self.sunk = False
        self.horizontal = True
    
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
            
            if result == 'hit':
                pygame.draw.circle(screen, self.colors['hit'],
                                 (cell_x + self.cell_size // 2, 
                                  cell_y + self.cell_size // 2), 
                                 self.cell_size // 3)
            elif result == 'miss':
                pygame.draw.circle(screen, self.colors['miss'],
                                 (cell_x + self.cell_size // 2, 
                                  cell_y + self.cell_size // 2), 
                                 self.cell_size // 4)
        
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
            
        hull_color = (80, 80, 80)
        deck_color = (120, 100, 80)
        detail_color = (60, 60, 60)
        hit_color = (255, 0, 0)
        
        margin = 3
        
        min_x = min(pos[0] for pos in ship.positions)
        max_x = max(pos[0] for pos in ship.positions)
        min_y = min(pos[1] for pos in ship.positions)
        max_y = max(pos[1] for pos in ship.positions)
        
        start_pixel_x = self.x + min_x * self.cell_size + margin
        start_pixel_y = self.y + min_y * self.cell_size + margin
        
        if ship.horizontal:
            ship_width = (max_x - min_x + 1) * self.cell_size - 2 * margin
            ship_height = self.cell_size - 2 * margin
            
            hull_rect = pygame.Rect(start_pixel_x, start_pixel_y + 8, ship_width, ship_height - 16)
            pygame.draw.ellipse(screen, hull_color, hull_rect)
            
            deck_rect = pygame.Rect(start_pixel_x + 3, start_pixel_y + 12, ship_width - 6, ship_height - 24)
            pygame.draw.ellipse(screen, deck_color, deck_rect)
            
            if ship.size >= 3:
                for i in range(0, ship.size, 2):
                    chimney_x = start_pixel_x + (i * self.cell_size) + self.cell_size // 3
                    chimney_rect = pygame.Rect(chimney_x, start_pixel_y + 5, 8, 12)
                    pygame.draw.rect(screen, detail_color, chimney_rect)
            
            if ship.size >= 4:
                for i in range(1, ship.size):
                    line_x = start_pixel_x + i * self.cell_size - margin
                    pygame.draw.line(screen, detail_color, 
                                   (line_x, start_pixel_y + 15), 
                                   (line_x, start_pixel_y + ship_height - 15), 1)
        else:
            ship_width = self.cell_size - 2 * margin
            ship_height = (max_y - min_y + 1) * self.cell_size - 2 * margin
            
            hull_rect = pygame.Rect(start_pixel_x + 8, start_pixel_y, ship_width - 16, ship_height)
            pygame.draw.ellipse(screen, hull_color, hull_rect)
            
            deck_rect = pygame.Rect(start_pixel_x + 12, start_pixel_y + 3, ship_width - 24, ship_height - 6)
            pygame.draw.ellipse(screen, deck_color, deck_rect)
            
            if ship.size >= 3:
                for i in range(0, ship.size, 2):
                    chimney_y = start_pixel_y + (i * self.cell_size) + self.cell_size // 3
                    chimney_rect = pygame.Rect(start_pixel_x + 5, chimney_y, 12, 8)
                    pygame.draw.rect(screen, detail_color, chimney_rect)
            
            if ship.size >= 4:
                for i in range(1, ship.size):
                    line_y = start_pixel_y + i * self.cell_size - margin
                    pygame.draw.line(screen, detail_color,
                                   (start_pixel_x + 15, line_y),
                                   (start_pixel_x + ship_width - 15, line_y), 1)
        
        for pos_x, pos_y in ship.positions:
            if (pos_x, pos_y) in ship.hits:
                hit_x = self.x + pos_x * self.cell_size + self.cell_size // 2
                hit_y = self.y + pos_y * self.cell_size + self.cell_size // 2
                
                pygame.draw.circle(screen, hit_color, (hit_x, hit_y), 8)
                pygame.draw.circle(screen, (255, 150, 0), (hit_x, hit_y), 5)
                pygame.draw.circle(screen, (255, 255, 0), (hit_x, hit_y), 3)
    
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
        preview_surface.set_alpha(120)
        preview_surface.fill((0, 0, 0, 0))
        
        temp_board = GameBoard(self.my_board.x, self.my_board.y, self.my_board.width)
        temp_board.ships = [temp_ship]
        temp_board.colors = self.my_board.colors.copy()
        
        if can_place:
            temp_board.colors['ship'] = (0, 200, 0)  # Verde
        else:
            temp_board.colors['ship'] = (200, 0, 0)
        
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
        
        if shooter == self.network_manager.player_id:
            # Registrar el disparo en el tablero enemigo
            self.enemy_board.shots[(x, y)] = result
            
            # Solo pierdo el turno si es miss
            if result == 'miss':
                self.my_turn = False
            # Si es hit o sunk, mantengo el turno para seguir disparando
            
        else:
            # El disparo fue del oponente hacia mi tablero
            # Registrar el impacto en mi tablero si es necesario
            # El servidor ya maneja la lógica de turno, solo actualizar UI
            pass
    
    def set_my_turn(self, is_my_turn):
        self.my_turn = is_my_turn
    
    def start_battle_phase(self):
        self.game_phase = "battle"