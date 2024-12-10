import pygame

def resize_image(img, factor):
        size = round(img.get_width() * factor), round(img.get_height() * factor)
        return pygame.transform.scale(img, size)

def blit_rotate_center(image, top_left, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topLeft=top_left).center)
    pygame.screen.blit(rotated_image, new_rect.topleft)