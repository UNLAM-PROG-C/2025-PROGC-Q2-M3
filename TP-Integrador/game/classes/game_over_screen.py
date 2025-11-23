"""
Pantalla de fin de juego para Batalla Naval
Muestra el resultado de la partida
"""

import pygame
import sys
import os

# Importar constants desde la carpeta padre del proyecto
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from constants import *

# Constantes específicas para GameOverScreen
BUTTON_VERTICAL_OFFSET = 100
SHADOW_OFFSET_X = 3
SHADOW_OFFSET_Y = 3
TEXT_VERTICAL_OFFSET = 50
BUTTON_BORDER_WIDTH = 3
MOUSE_LEFT_BUTTON = 1
GAME_OVER_DIVISION_FACTOR = 2
AUTO_RETURN_TIMEOUT = 5000   # 5 segundos en milisegundos
COUNTDOWN_Y_OFFSET = 80      # Espacio debajo del botón para mostrar countdown

class GameOverScreen:
    """Pantalla de fin de juego que muestra el resultado de la partida."""
    
    def __init__(self, screen, is_winner=False):
        """Inicializa la pantalla de game over.
        
        Args:
            screen: Superficie de pygame para dibujar
            is_winner: True si el jugador ganó, False si perdió
        """
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.is_winner = is_winner
        
        # Configurar timeout automático
        self.start_time = pygame.time.get_ticks()
        self.auto_return = False
        
        self._setup_button()
        self._setup_fonts()
    
    def _setup_button(self):
        """Configura las propiedades del botón ACEPTAR."""
        button_x = self._calculate_button_x_position()
        button_y = self._calculate_button_y_position()
        
        self.accept_button = {
            'rect': pygame.Rect(button_x, button_y, GAME_OVER_BUTTON_WIDTH, GAME_OVER_BUTTON_HEIGHT),
            'text': 'ACEPTAR',
            'color': COLOR_BUTTON_CONNECT,
            'hover_color': COLOR_BUTTON_CONNECT_HOVER,
            'text_color': COLOR_WHITE
        }
    
    def _calculate_button_x_position(self):
        """Calcula la posición X centrada del botón.
        
        Returns:
            int: Posición X del botón
        """
        return self.width // GAME_OVER_DIVISION_FACTOR - GAME_OVER_BUTTON_WIDTH // GAME_OVER_DIVISION_FACTOR
    
    def _calculate_button_y_position(self):
        """Calcula la posición Y del botón.
        
        Returns:
            int: Posición Y del botón
        """
        return self.height // GAME_OVER_DIVISION_FACTOR + BUTTON_VERTICAL_OFFSET
    
    def _setup_fonts(self):
        """Configura las fuentes utilizadas en la pantalla."""
        self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_SIZE_DIALOG_TITLE)
        self.font_small = pygame.font.Font(None, FONT_SIZE_NORMAL)
        self.font_countdown = pygame.font.Font(None, FONT_SIZE_DIALOG_TITLE + 5)  # Fuente más grande para countdown
    
    def handle_event(self, event):
        """Maneja los eventos de entrada del usuario.
        
        Args:
            event: Evento de pygame a procesar
            
        Returns:
            str o None: 'accept' si se hizo click en el botón o timeout, None en caso contrario
        """
        # Verificar timeout automático
        if self._check_auto_timeout():
            return "accept"
            
        if self._is_mouse_click_event(event):
            return self._handle_mouse_click()
        return None
    
    def _is_mouse_click_event(self, event):
        """Verifica si el evento es un click izquierdo del mouse.
        
        Args:
            event: Evento de pygame a verificar
            
        Returns:
            bool: True si es click izquierdo, False en caso contrario
        """
        return (event.type == pygame.MOUSEBUTTONDOWN and 
                event.button == MOUSE_LEFT_BUTTON)
    
    def _handle_mouse_click(self):
        """Procesa el click del mouse y verifica si fue en el botón.
        
        Returns:
            str o None: 'accept' si se hizo click en el botón, None en caso contrario
        """
        mouse_pos = pygame.mouse.get_pos()
        if self.accept_button['rect'].collidepoint(mouse_pos):
            return "accept"
        return None
    
    def _check_auto_timeout(self):
        """Verifica si ha pasado el tiempo para volver automáticamente al menú.
        
        Returns:
            bool: True si debe volver al menú automáticamente
        """
        elapsed_time = pygame.time.get_ticks() - self.start_time
        if elapsed_time >= AUTO_RETURN_TIMEOUT:
            self.auto_return = True
            return True
        return False
    
    def _get_remaining_seconds(self):
        """Calcula los segundos restantes para el retorno automático.
        
        Returns:
            int: Segundos restantes (mínimo 0)
        """
        elapsed_time = pygame.time.get_ticks() - self.start_time
        remaining_ms = max(0, AUTO_RETURN_TIMEOUT - elapsed_time)
        return max(0, int(remaining_ms / 1000) + 1)
    
    def draw(self):
        """Dibuja todos los elementos de la pantalla de game over."""
        self._draw_overlay()
        self._draw_main_text()
        self._draw_button()
        self._draw_countdown_if_needed()
    
    def _draw_overlay(self):
        """Dibuja el fondo semi-transparente."""
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(GAME_OVER_ALPHA)
        overlay.fill(COLOR_BLACK)
        self.screen.blit(overlay, (0, 0))
    
    def _draw_main_text(self):
        """Dibuja el texto principal (GANASTE/PERDISTE) con sombra."""
        main_text, text_color = self._get_main_text_and_color()
        
        shadow_surface = self.font_large.render(main_text, True, COLOR_BLACK)
        text_surface = self.font_large.render(main_text, True, text_color)
        
        text_center_x, text_center_y = self._get_text_center_position()
        
        text_rect = text_surface.get_rect(center=(text_center_x, text_center_y))
        shadow_rect = self._get_shadow_rect(text_center_x, text_center_y)
        
        self.screen.blit(shadow_surface, shadow_rect)
        self.screen.blit(text_surface, text_rect)
    
    def _get_main_text_and_color(self):
        """Determina el texto y color principal basado en el resultado.
        
        Returns:
            tuple: (texto, color) para mostrar
        """
        return ("GANASTE", COLOR_GREEN) if self.is_winner else ("PERDISTE", COLOR_RED)
    
    def _get_text_center_position(self):
        """Calcula la posición centrada del texto principal.
        
        Returns:
            tuple: (x, y) para el centro del texto
        """
        center_x = self.width // GAME_OVER_DIVISION_FACTOR
        center_y = self.height // GAME_OVER_DIVISION_FACTOR - TEXT_VERTICAL_OFFSET
        return center_x, center_y
    
    def _get_shadow_rect(self, text_center_x, text_center_y):
        """Calcula la posición del rectángulo de sombra del texto.
        
        Args:
            text_center_x: Posición X del centro del texto
            text_center_y: Posición Y del centro del texto
            
        Returns:
            pygame.Rect: Rectángulo para la sombra
        """
        shadow_x = text_center_x + SHADOW_OFFSET_X
        shadow_y = text_center_y + SHADOW_OFFSET_Y
        
        # Crear superficie temporal para obtener dimensiones
        main_text, _ = self._get_main_text_and_color()
        temp_surface = self.font_large.render(main_text, True, COLOR_BLACK)
        return temp_surface.get_rect(center=(shadow_x, shadow_y))
    
    def _draw_button(self):
        """Dibuja el botón ACEPTAR con hover effect."""
        button_color = self._get_button_color()
        
        pygame.draw.rect(self.screen, button_color, self.accept_button['rect'])
        pygame.draw.rect(self.screen, COLOR_WHITE, self.accept_button['rect'], BUTTON_BORDER_WIDTH)
        
        self._draw_button_text()
    
    def _get_button_color(self):
        """Determina el color del botón basado en el hover.
        
        Returns:
            tuple: Color RGB para el botón
        """
        mouse_pos = pygame.mouse.get_pos()
        return (self.accept_button['hover_color'] 
                if self.accept_button['rect'].collidepoint(mouse_pos) 
                else self.accept_button['color'])
    
    def _draw_button_text(self):
        """Dibuja el texto del botón centrado."""
        button_text = self.font_medium.render(
            self.accept_button['text'], 
            True, 
            self.accept_button['text_color']
        )
        button_text_rect = button_text.get_rect(center=self.accept_button['rect'].center)
        self.screen.blit(button_text, button_text_rect)
    
    def _draw_countdown_if_needed(self):
        """Dibuja el mensaje de cuenta regresiva desde el inicio con texto más grande y visible."""
        elapsed_time = pygame.time.get_ticks() - self.start_time
        remaining_total_seconds = (AUTO_RETURN_TIMEOUT - elapsed_time) / 1000
        
        if remaining_total_seconds > 0:
            remaining_seconds = self._get_remaining_seconds()
            countdown_text = f"Volviendo al menú principal en {remaining_seconds} segundos"
            
            # Renderiza el texto de countdown con fuente más grande
            countdown_surface = self.font_countdown.render(countdown_text, True, pygame.Color('orange'))
            countdown_rect = countdown_surface.get_rect()
            countdown_rect.centerx = self.width // 2
            countdown_rect.y = self.accept_button['rect'].bottom + COUNTDOWN_Y_OFFSET
            
            # Dibuja fondo más prominente para el texto
            padding = 15
            bg_rect = pygame.Rect(countdown_rect.x - padding, countdown_rect.y - padding,
                                countdown_rect.width + 2*padding, countdown_rect.height + 2*padding)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
            bg_surface.set_alpha(180)  # Más opaco para mejor visibilidad
            bg_surface.fill(COLOR_BLACK)
            self.screen.blit(bg_surface, bg_rect.topleft)
            
            # Dibuja borde para mayor visibilidad
            pygame.draw.rect(self.screen, pygame.Color('orange'), bg_rect, 2)
            
            # Dibuja el texto de countdown
            self.screen.blit(countdown_surface, countdown_rect)