import pygame
# ===== sound play =====
def play_sound(file):
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()