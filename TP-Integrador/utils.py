import pygame
import os

class Colors:
    """Constantes de colores para el juego"""
    WATER = (100, 149, 237)
    SHIP = (139, 69, 19)
    HIT = (255, 0, 0)
    MISS = (255, 255, 255)
    GRID = (0, 0, 0)
    BACKGROUND = (30, 60, 90)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)

def load_image(path, scale=None):
    """Cargar una imagen con manejo de errores"""
    try:
        image = pygame.image.load(path)
        if scale:
            image = pygame.transform.scale(image, scale)
        return image
    except pygame.error as e:
        print(f"No se pudo cargar la imagen {path}: {e}")
        return None

def draw_text(screen, text, font_size, color, x, y, center=False):
    """Dibujar texto en la pantalla"""
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    
    if center:
        text_rect = text_surface.get_rect(center=(x, y))
        screen.blit(text_surface, text_rect)
    else:
        screen.blit(text_surface, (x, y))
    
    return text_surface.get_rect()

def coords_to_chess_notation(x, y):
    """Convertir coordenadas (x, y) a notación de ajedrez (A1, B2, etc.)"""
    if 0 <= x < 10 and 0 <= y < 10:
        col = chr(ord('A') + x)
        row = str(y + 1)
        return f"{col}{row}"
    return "??"

def chess_notation_to_coords(notation):
    """Convertir notación de ajedrez a coordenadas (x, y)"""
    if len(notation) >= 2:
        col = notation[0].upper()
        row = notation[1:]
        try:
            x = ord(col) - ord('A')
            y = int(row) - 1
            if 0 <= x < 10 and 0 <= y < 10:
                return (x, y)
        except ValueError:
            pass
    return None

class Button:
    """Clase para crear botones interactivos"""
    def __init__(self, x, y, width, height, text, color=(100, 100, 100), 
                 text_color=(255, 255, 255), font_size=36):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = tuple(min(255, c + 50) for c in color)
        self.text_color = text_color
        self.font = pygame.font.Font(None, font_size)
        self.enabled = True
        
    def draw(self, screen):
        # Determinar color basado en estado
        if not self.enabled:
            color = tuple(c // 2 for c in self.color)  # Más oscuro si deshabilitado
        elif self.is_hovered():
            color = self.hover_color
        else:
            color = self.color
            
        # Dibujar botón
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        
        # Dibujar texto
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def is_hovered(self):
        """Verificar si el mouse está sobre el botón"""
        return self.rect.collidepoint(pygame.mouse.get_pos())
    
    def is_clicked(self, mouse_pos):
        """Verificar si se hizo click en el botón"""
        return self.enabled and self.rect.collidepoint(mouse_pos)

def create_gradient_surface(width, height, start_color, end_color):
    """Crear una superficie con gradiente vertical"""
    surface = pygame.Surface((width, height))
    
    for y in range(height):
        ratio = y / height
        r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
        g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
        b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
        
        pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
    
    return surface