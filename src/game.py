# game.py
import pygame
import sys
import os
from pygame import mixer
import random
import math

class BusinessClicker:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()  # Pour le son
        
        # Configuration de l'écran
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.width = self.screen.get_width()
        self.height = self.screen.get_height()
        pygame.display.set_caption("Business Clicker")
        
        # Paramètres du jeu
        self.money = 0
        self.click_value = 1
        self.font = pygame.font.Font(None, 64)  # Police plus grande pour le score
        
        # Chargement des assets
        self.load_assets()
        
        # Création du document clickable
        self.document_scale = 4  # Échelle du pixel art
        scaled_width = self.document.get_width() * self.document_scale
        scaled_height = self.document.get_height() * self.document_scale
        self.document = pygame.transform.scale(self.document, (scaled_width, scaled_height))
        
        # Position du document (centré)
        self.document_rect = self.document.get_rect()
        self.document_rect.center = (self.width // 2, self.height // 2)
        
        # Configuration du son
        mixer.init()
        mixer.set_num_channels(3)  # Pour éviter la superposition des sons
        self.sound_cooldown = 0  # Pour éviter la répétition trop rapide

        # Meilleurs paramètres d'animation
        self.click_animation = False
        self.animation_frame = 0
        self.animation_max_frame = 10  # Animation plus longue pour plus de fluidité
        self.animation_scale = 1.0
        
        # État initial du document
        self.original_document_pos = self.document_rect.center
        
    def load_assets(self):
        # Chargement du fond
        self.background = pygame.image.load(os.path.join('assets', 'images', 'office_background.png'))
        self.background = pygame.transform.scale(self.background, (self.width, self.height))
        
        # Chargement et redimensionnement du document
        original_document = pygame.image.load(os.path.join('assets', 'images', 'document_pixel.png'))
        # Définir une taille raisonnable pour le document (par exemple 10% de la hauteur de l'écran)
        document_size = int(self.height * 0.1)  # ou une autre valeur qui vous convient
        self.document = pygame.transform.scale(original_document, (document_size, document_size))
        
        # Chargement et configuration du son
        self.click_sound = mixer.Sound(os.path.join('assets', 'sounds', 'paper_shuffle.wav'))
        # Réduire le volume (0.0 à 1.0)
        self.click_sound.set_volume(0.3)

        # Création du rectangle pour le document (centré)
        self.document_rect = self.document.get_rect()
        self.document_rect.center = (self.width // 2, self.height // 2)
        
    def handle_click(self, pos):
        current_time = pygame.time.get_ticks()
        if (self.document_rect.collidepoint(pos) and 
            not self.click_animation and 
            current_time > self.sound_cooldown):
            
            self.money += self.click_value
            
            # Jouer le son avec une variation aléatoire
            # Choisir aléatoirement le début du son
            start_time = random.choice([0, 500])  # milliseconds
            channel = mixer.find_channel(True)  # Trouver un canal libre
            if channel:
                channel.play(self.click_sound, maxtime=500)  # Ne jouer que 500ms du son
                channel.set_volume(0.3)  # Volume réduit
            
            self.click_animation = True
            self.animation_frame = 0
            self.sound_cooldown = current_time + 100  # 100ms de cooldown
    
def update_animation(self):
    if self.click_animation:
        self.animation_frame += 1
        if self.animation_frame >= self.animation_max_frame:
            self.click_animation = False
            self.animation_frame = 0
            return

        # Simple réduction puis retour à la normale
        if self.animation_frame < self.animation_max_frame / 2:
            scale = 0.9  # Réduit à 90% de la taille
        else:
            scale = 1.0  # Retour à la taille normale
            
        # Appliquer l'échelle
        original_size = self.document.get_rect().size
        scaled_size = (int(original_size[0] * scale), int(original_size[1] * scale))
        scaled_doc = pygame.transform.scale(self.document, scaled_size)
        
        # Garder le document centré
        old_center = self.document_rect.center
        self.document_rect = scaled_doc.get_rect(center=old_center)
        
    def draw(self):
        # Dessin du fond
        self.screen.blit(self.background, (0, 0))
        
        # Dessin du document
        self.screen.blit(self.document, self.document_rect)
        
        # Affichage de l'argent
        money_text = self.font.render(f"€{self.money}", True, (50, 50, 50))
        money_rect = money_text.get_rect(topleft=(20, 20))
        
        # Ombre du texte pour meilleure lisibilité
        shadow_text = self.font.render(f"€{self.money}", True, (200, 200, 200))
        shadow_rect = shadow_text.get_rect(topleft=(22, 22))
        self.screen.blit(shadow_text, shadow_rect)
        self.screen.blit(money_text, money_rect)
        
        pygame.display.flip()
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Clic gauche
                        self.handle_click(event.pos)
            
            self.update_animation()
            self.draw()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()
