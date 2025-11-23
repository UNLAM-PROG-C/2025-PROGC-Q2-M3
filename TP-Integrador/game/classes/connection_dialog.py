import pygame
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from constants import *

DIALOG_CENTER_DIVISION_FACTOR = 2
HOST_INPUT_Y_OFFSET = -80
PORT_INPUT_Y_OFFSET = 10
BUTTONS_Y_OFFSET = 100
BUTTON_SPACING = 20
BUTTON_SEPARATION = 10
TITLE_Y_POSITION = 120
SUBTITLE_Y_POSITION = 170
OVERLAY_DARK_COLOR = (0, 0, 20)
DIALOG_BACKGROUND_COLOR = (30, 30, 60)
FIELD_BORDER_RADIUS = 3
BUTTON_BORDER_RADIUS = 5
FIELD_BORDER_WIDTH = 2
BUTTON_BORDER_WIDTH = 2
CURSOR_THICKNESS = 2
CURSOR_HEIGHT_OFFSET = 15
TEXT_LEFT_MARGIN = 10
LABEL_RIGHT_MARGIN = 10
CURSOR_RIGHT_MARGIN = 2
FIELD_ACTIVE_BORDER_COLOR = (100, 200, 255)
FIELD_INACTIVE_BORDER_COLOR = (255, 255, 255)
PLACEHOLDER_COLOR = (120, 120, 120)
FIELD_BACKGROUND_COLOR = (200, 200, 200)

class ConnectionDialog:
    
    def __init__(self, screen):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        self._initialize_clipboard()
        self._initialize_state()
        self._initialize_ui()
    
    def _initialize_clipboard(self):
        try:
            pygame.scrap.init()
            print("Módulo de portapapeles inicializado correctamente")
        except Exception as e:
            print(f"Error al inicializar portapapeles: {e}")
    
    def _initialize_state(self):
        self.active = True
        self.result = None
        self.host_input = ''
        self.port_input = ''
        self.active_input = 'host'
    
    def _initialize_ui(self):
        self.menu_image = None
        self.load_menu_background()
        self._setup_fonts()
        self.setup_ui()
    
    def _setup_fonts(self):
        self.font_title = pygame.font.Font(None, FONT_SIZE_DIALOG_TITLE)
        self.font_normal = pygame.font.Font(None, FONT_SIZE_NORMAL)
        self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)
    
    def load_menu_background(self):
        try:
            self.menu_image = pygame.image.load('assets/images/menu.png')
            self.menu_image = pygame.transform.scale(self.menu_image, (self.width, self.height))
        except pygame.error:
            self.menu_image = None
    
    def draw_menu_background(self):
        if self.menu_image:
            self.screen.blit(self.menu_image, (0, 0))
        else:
            self.screen.fill(DIALOG_BACKGROUND_COLOR)
        
    def setup_ui(self):
        center_x = self.width // DIALOG_CENTER_DIVISION_FACTOR
        center_y = self.height // DIALOG_CENTER_DIVISION_FACTOR
        
        self._setup_input_fields(center_x, center_y)
        self._setup_action_buttons(center_x, center_y)
        self._setup_default_values()
    
    def _setup_input_fields(self, center_x, center_y):
        self.host_field = {
            'rect': pygame.Rect(center_x - CONNECTION_INPUT_WIDTH//DIALOG_CENTER_DIVISION_FACTOR, 
                              center_y + HOST_INPUT_Y_OFFSET, CONNECTION_INPUT_WIDTH, CONNECTION_INPUT_HEIGHT),
            'label': 'Host / IP:',
            'name': 'host',
            'placeholder': 'localhost o 192.168.1.xxx',
            'color': FIELD_BACKGROUND_COLOR,
            'active_color': COLOR_WHITE,
            'text_color': COLOR_BLACK
        }
        
        self.port_field = {
            'rect': pygame.Rect(center_x - CONNECTION_INPUT_WIDTH//DIALOG_CENTER_DIVISION_FACTOR, 
                              center_y + PORT_INPUT_Y_OFFSET, CONNECTION_INPUT_WIDTH, CONNECTION_INPUT_HEIGHT),
            'label': 'Puerto:',
            'name': 'port',
            'placeholder': '8888',
            'color': FIELD_BACKGROUND_COLOR,
            'active_color': COLOR_WHITE,
            'text_color': COLOR_BLACK
        }
    
    def _setup_action_buttons(self, center_x, center_y):
        self.connect_button = {
            'rect': pygame.Rect(center_x - CONNECTION_BUTTON_WIDTH - BUTTON_SEPARATION, 
                              center_y + BUTTONS_Y_OFFSET, CONNECTION_BUTTON_WIDTH, CONNECTION_BUTTON_HEIGHT),
            'text': 'Conectar',
            'color': COLOR_BUTTON_CONNECT,
            'hover_color': COLOR_BUTTON_CONNECT_HOVER
        }
        
        self.cancel_button = {
            'rect': pygame.Rect(center_x + BUTTON_SEPARATION, 
                              center_y + BUTTONS_Y_OFFSET, CONNECTION_BUTTON_WIDTH, CONNECTION_BUTTON_HEIGHT),
            'text': 'Cancelar',
            'color': COLOR_BUTTON_CANCEL,
            'hover_color': COLOR_BUTTON_CANCEL_HOVER
        }
    
    def _setup_default_values(self):
        self.port_input = str(DEFAULT_SERVER_PORT)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_click(event)
        elif event.type == pygame.KEYDOWN:
            self._handle_key_press(event)
    
    def _handle_mouse_click(self, event):
        if self.host_field['rect'].collidepoint(event.pos):
            self.active_input = 'host'
        elif self.port_field['rect'].collidepoint(event.pos):
            self.active_input = 'port'
        elif self.connect_button['rect'].collidepoint(event.pos):
            self._handle_connect()
        elif self.cancel_button['rect'].collidepoint(event.pos):
            self._handle_cancel()
    
    def _handle_key_press(self, event):
        if event.key == pygame.K_ESCAPE:
            self._handle_cancel()
        else:
            self._handle_text_input(event)
    
    def _handle_connect(self):
        if not self._validate_host():
            return
        
        port = self._validate_and_get_port()
        if port is None:
            return
        
        self._complete_connection(port)
    
    def _validate_host(self):
        if not self.host_input.strip():
            print("Host vacío - necesitas ingresar una IP")
            return False
        return True
    
    def _validate_and_get_port(self):
        if not self.port_input.strip():
            print("Puerto vacío - usando puerto por defecto")
            self.port_input = str(DEFAULT_SERVER_PORT)
        
        try:
            port = int(self.port_input.strip())
            if not (MIN_PORT_NUMBER <= port <= MAX_PORT_NUMBER):
                print(f"Puerto fuera de rango válido ({MIN_PORT_NUMBER}-{MAX_PORT_NUMBER})")
                return None
            return port
        except ValueError:
            print("Puerto inválido - debe ser un número")
            return None
    
    def _complete_connection(self, port):
        self.result = {
            'host': self.host_input.strip(),
            'port': port
        }
        self.active = False
        print(f"Conectando a {self.result['host']}:{self.result['port']}")
    
    def _handle_cancel(self):
        self.result = None
        self.active = False
    
    def _handle_text_input(self, event):
        if self.active_input == 'host':
            self._handle_host_input(event)
        elif self.active_input == 'port':
            self._handle_port_input(event)
    
    def _handle_host_input(self, event):
        if event.key == pygame.K_BACKSPACE:
            self.host_input = self.host_input[:-1]
        elif self._is_paste_command(event):
            self._handle_paste_clipboard()
        elif event.key == pygame.K_TAB:
            self.active_input = 'port'
        elif event.key == pygame.K_RETURN:
            self._handle_connect()
        elif self._is_valid_host_char(event):
            self.host_input += event.unicode
    
    def _is_paste_command(self, event):
        return (event.key == pygame.K_v and 
                pygame.key.get_pressed()[pygame.K_LCTRL])
    
    def _handle_paste_clipboard(self):
        try:
            clipboard_text = pygame.scrap.get(pygame.SCRAP_TEXT)
            if clipboard_text:
                pasted_text = clipboard_text.decode('utf-8').strip()
                valid_chars = ''.join(c for c in pasted_text if c.isalnum() or c in '.-_')
                if valid_chars and len(self.host_input + valid_chars) <= MAX_HOST_LENGTH:
                    self.host_input += valid_chars
                    print(f"📋 Pegado desde portapapeles: {valid_chars}")
        except Exception as e:
            print(f"Error al pegar: {e}")
    
    def _is_valid_host_char(self, event):
        return (event.unicode and 
                (event.unicode.isalnum() or event.unicode in '.-_') and 
                len(self.host_input) < MAX_HOST_LENGTH)
    
    def _handle_port_input(self, event):
        if event.key == pygame.K_BACKSPACE:
            self.port_input = self.port_input[:-1]
        elif event.key == pygame.K_TAB:
            self.active_input = 'host'
        elif event.key == pygame.K_RETURN:
            self._handle_connect()
        elif self._is_valid_port_char(event):
            self.port_input += event.unicode
    
    def _is_valid_port_char(self, event):
        return (event.unicode.isdigit() and 
                len(self.port_input) < MAX_PORT_LENGTH)
    
    def draw(self):
        self.draw_menu_background()
        self._draw_overlay()
        self._draw_title_and_subtitle()
        self._draw_input_fields()
        self._draw_action_buttons()
    
    def _draw_overlay(self):
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(OVERLAY_ALPHA)
        overlay.fill(OVERLAY_DARK_COLOR)
        self.screen.blit(overlay, (0, 0))
    
    def _draw_title_and_subtitle(self):
        title = self.font_title.render("Conectar al Servidor", True, COLOR_WHITE)
        title_rect = title.get_rect(center=(self.width//DIALOG_CENTER_DIVISION_FACTOR, TITLE_Y_POSITION))
        self.screen.blit(title, title_rect)
        
        subtitle = self.font_small.render("Ingresa la dirección del servidor:", True, FIELD_BACKGROUND_COLOR)
        subtitle_rect = subtitle.get_rect(center=(self.width//DIALOG_CENTER_DIVISION_FACTOR, SUBTITLE_Y_POSITION))
        self.screen.blit(subtitle, subtitle_rect)

    def _draw_input_fields(self):
        mouse_pos = pygame.mouse.get_pos()
        
        for field in [self.host_field, self.port_field]:
            self._draw_single_field(field, mouse_pos)
    
    def _draw_single_field(self, field, mouse_pos):
        color, border_color = self._get_field_colors(field)
        
        pygame.draw.rect(self.screen, color, field['rect'], border_radius=FIELD_BORDER_RADIUS)
        pygame.draw.rect(self.screen, border_color, field['rect'], FIELD_BORDER_WIDTH, border_radius=FIELD_BORDER_RADIUS)
        
        self._draw_field_label(field)
        self._draw_field_content(field)
    
    def _get_field_colors(self, field):
        if self.active_input == field['name']:
            color = field['active_color']
            border_color = FIELD_ACTIVE_BORDER_COLOR
        else:
            color = field['color']
            border_color = FIELD_INACTIVE_BORDER_COLOR
        return color, border_color
    
    def _draw_field_label(self, field):
        label = self.font_small.render(field['label'], True, FIELD_BACKGROUND_COLOR)
        label_rect = label.get_rect(midright=(field['rect'].left - LABEL_RIGHT_MARGIN, field['rect'].centery))
        self.screen.blit(label, label_rect)
    
    def _draw_field_content(self, field):
        text_value = self.host_input if field['name'] == 'host' else self.port_input
        
        if not text_value:
            self._draw_placeholder(field)
        else:
            self._draw_field_text(field, text_value)
    
    def _draw_placeholder(self, field):
        placeholder = self.font_normal.render(field['placeholder'], True, PLACEHOLDER_COLOR)
        placeholder_rect = placeholder.get_rect(midleft=(field['rect'].left + TEXT_LEFT_MARGIN, field['rect'].centery))
        self.screen.blit(placeholder, placeholder_rect)
    
    def _draw_field_text(self, field, text_value):
        text = self.font_normal.render(text_value, True, COLOR_BLACK)
        text_rect = text.get_rect(midleft=(field['rect'].left + TEXT_LEFT_MARGIN, field['rect'].centery))
        self.screen.blit(text, text_rect)
        
        if field['name'] == self.active_input and pygame.time.get_ticks() % 1000 < 500:
            cursor_x = text_rect.right + CURSOR_RIGHT_MARGIN
            cursor_y_start = field['rect'].centery - CURSOR_HEIGHT_OFFSET
            cursor_y_end = field['rect'].centery + CURSOR_HEIGHT_OFFSET
            pygame.draw.line(self.screen, COLOR_BLACK, (cursor_x, cursor_y_start), (cursor_x, cursor_y_end), CURSOR_THICKNESS)
    
    def _draw_action_buttons(self):
        mouse_pos = pygame.mouse.get_pos()
        
        for button in [self.connect_button, self.cancel_button]:
            self._draw_single_button(button, mouse_pos)
    
    def _draw_single_button(self, button, mouse_pos):
        if button['rect'].collidepoint(mouse_pos):
            color = button['hover_color']
        else:
            color = button['color']
        
        pygame.draw.rect(self.screen, color, button['rect'], border_radius=BUTTON_BORDER_RADIUS)
        pygame.draw.rect(self.screen, COLOR_WHITE, button['rect'], BUTTON_BORDER_WIDTH, border_radius=BUTTON_BORDER_RADIUS)
        
        text = self.font_normal.render(button['text'], True, COLOR_WHITE)
        text_rect = text.get_rect(center=button['rect'].center)
        self.screen.blit(text, text_rect)
        
    def run(self):
        clock = pygame.time.Clock()
        
        while self.active:
            self._process_events()
            self.draw()
            pygame.display.flip()
            clock.tick(TARGET_FPS)
        
        return self.result
    
    def _process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            self.handle_event(event)