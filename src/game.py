import pygame
import sys
import os
from pygame import mixer
import random
import math
from typing import List, Dict
import json
from models import Upgrade

class BusinessClicker:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Screen setup
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.width = self.screen.get_width()
        self.height = self.screen.get_height()
        pygame.display.set_caption("Business Clicker")
        
        # Game state
        self.money = 0
        self.click_value = 1
        self.passive_income = 0
        self.last_passive_update = pygame.time.get_ticks()
        
        # UI setup
        self.font_large = pygame.font.Font(None, 64)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # Initialize upgrades
        self.upgrades = self.initialize_upgrades()
        self.selected_upgrade = None
        
        # Load assets
        self.load_assets()
        self.setup_ui()
        
        # Animation state
        self.click_animation = False
        self.animation_frame = 0
        self.animation_max_frame = 10
        self.particles = []
        
        # Statistics
        self.stats = {
            'total_clicks': 0,
            'total_money_earned': 0,
            'total_upgrades_bought': 0
        }
        
        # Load saved game if exists
        self.load_game()
        
    def initialize_upgrades(self) -> List[Upgrade]:
        return [
            Upgrade("Coffee Machine", 10, 0.1, "Each coffee increases productivity"),
            Upgrade("Intern", 50, 0.5, "They work... sometimes"),
            Upgrade("Office Computer", 200, 2, "Faster document processing"),
            Upgrade("Automated Scanner", 1000, 10, "Scan documents automatically"),
            Upgrade("AI Assistant", 5000, 50, "Next-gen productivity boost")
        ]
    
    def load_assets(self):
        # Load and scale background
        self.background = pygame.image.load(os.path.join('assets', 'images', 'office_background.png'))
        self.background = pygame.transform.scale(self.background, (self.width, self.height))
        
        # Load and scale document
        document_size = int(self.height * 0.15)
        original_document = pygame.image.load(os.path.join('assets', 'images', 'document_pixel.png'))
        self.document = pygame.transform.scale(original_document, (document_size, document_size))
        self.document_rect = self.document.get_rect(center=(self.width // 2, self.height // 2))
        
        # Load sounds with lower volume
        self.click_sound = mixer.Sound(os.path.join('assets', 'sounds', 'paper_shuffle.wav'))
        self.click_sound.set_volume(0.2)
        
        # Load upgrade icons (assuming you have these assets)
        self.upgrade_icons = {}
        for upgrade in self.upgrades:
            icon_path = os.path.join('assets', 'images', f'{upgrade.name.lower().replace(" ", "_")}.png')
            if os.path.exists(icon_path):
                self.upgrade_icons[upgrade.name] = pygame.image.load(icon_path)
            else:
                # Create a default colored rectangle as icon
                icon = pygame.Surface((32, 32))
                icon.fill((random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)))
                self.upgrade_icons[upgrade.name] = icon
    
    def setup_ui(self):
        # Create UI regions
        self.upgrade_region = pygame.Rect(self.width - 300, 0, 300, self.height)
        self.stats_region = pygame.Rect(0, 0, 300, 100)
        
        # Create buttons for upgrades
        self.upgrade_buttons = []
        for i, upgrade in enumerate(self.upgrades):
            button_rect = pygame.Rect(
                self.upgrade_region.x + 10,
                100 + i * 70,
                280,
                60
            )
            self.upgrade_buttons.append((button_rect, upgrade))

    def create_particles(self, pos, count=5):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 5)
            lifetime = random.randint(20, 40)
            self.particles.append({
                'pos': list(pos),
                'vel': [math.cos(angle) * speed, math.sin(angle) * speed],
                'lifetime': lifetime,
                'max_lifetime': lifetime,
                'text': '+' + str(self.click_value)
            })

    def update_particles(self):
        for particle in self.particles[:]:
            particle['pos'][0] += particle['vel'][0]
            particle['pos'][1] += particle['vel'][1]
            particle['lifetime'] -= 1
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
        
    def update_animation(self):
        if self.click_animation:
            self.animation_frame += 1
            if self.animation_frame >= self.animation_max_frame:
                self.click_animation = False
                self.animation_frame = 0

    def handle_click(self, pos):
        current_time = pygame.time.get_ticks()
        
        # Handle document click
        if self.document_rect.collidepoint(pos):
            self.money += self.click_value
            self.stats['total_clicks'] += 1
            self.stats['total_money_earned'] += self.click_value
            
            # Animation and effects
            self.click_animation = True
            self.animation_frame = 0
            self.create_particles(pos)
            
            channel = mixer.find_channel(True)
            if channel:
                channel.play(self.click_sound, maxtime=500)
        
        # Handle upgrade buttons
        for button, upgrade in self.upgrade_buttons:
            if button.collidepoint(pos):
                self.try_purchase_upgrade(upgrade)
                
    def try_purchase_upgrade(self, upgrade):
        if self.money >= upgrade.cost:
            self.money -= upgrade.cost
            upgrade.count += 1
            self.passive_income += upgrade.productivity_boost
            self.stats['total_upgrades_bought'] += 1
            
            # Increase cost for next purchase
            upgrade.cost = int(upgrade.cost * 1.15)

    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Update passive income
        time_diff = (current_time - self.last_passive_update) / 1000.0  # Convert to seconds
        earned = self.passive_income * time_diff
        self.money += earned
        self.stats['total_money_earned'] += earned
        self.last_passive_update = current_time
        
        # Update animations
        self.update_animation()
        self.update_particles()
        
    def draw_upgrade_panel(self):
        # Draw panel background
        pygame.draw.rect(self.screen, (240, 240, 240), self.upgrade_region)
        
        # Draw upgrades
        for button, upgrade in self.upgrade_buttons:
            # Button background
            color = (200, 200, 200) if self.money >= upgrade.cost else (150, 150, 150)
            pygame.draw.rect(self.screen, color, button, border_radius=5)
            
            # Draw upgrade icon
            icon = self.upgrade_icons[upgrade.name]
            icon_rect = icon.get_rect(midleft=(button.x + 10, button.centery))
            self.screen.blit(icon, icon_rect)
            
            # Draw upgrade info
            name_text = self.font_small.render(upgrade.name, True, (0, 0, 0))
            cost_text = self.font_small.render(f"€{upgrade.cost}", True, (0, 0, 0))
            count_text = self.font_small.render(f"x{upgrade.count}", True, (0, 0, 0))
            
            self.screen.blit(name_text, (button.x + 50, button.y + 10))
            self.screen.blit(cost_text, (button.x + 50, button.y + 30))
            self.screen.blit(count_text, (button.right - 50, button.centery))

    def draw_stats(self):
        # Draw stats background
        pygame.draw.rect(self.screen, (240, 240, 240), self.stats_region)
        
        # Draw money
        money_text = self.font_large.render(f"€{int(self.money)}", True, (0, 0, 0))
        self.screen.blit(money_text, (20, 20))
        
        # Draw passive income
        income_text = self.font_medium.render(f"€{self.passive_income:.1f}/s", True, (0, 100, 0))
        self.screen.blit(income_text, (20, 70))

    def draw_particles(self):
        for particle in self.particles:
            alpha = int(255 * (particle['lifetime'] / particle['max_lifetime']))
            text = self.font_small.render(particle['text'], True, (0, 200, 0))
            text.set_alpha(alpha)
            self.screen.blit(text, particle['pos'])

    def draw(self):
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw document
        self.screen.blit(self.document, self.document_rect)
        
        # Draw UI elements
        self.draw_upgrade_panel()
        self.draw_stats()
        self.draw_particles()
        
        pygame.display.flip()

    def save_game(self):
        save_data = {
            'money': self.money,
            'click_value': self.click_value,
            'passive_income': self.passive_income,
            'stats': self.stats,
            'upgrades': [(u.name, u.count, u.cost) for u in self.upgrades]
        }
        
        with open('save_game.json', 'w') as f:
            json.dump(save_data, f)

    def load_game(self):
        try:
            with open('save_game.json', 'r') as f:
                data = json.load(f)
                self.money = data['money']
                self.click_value = data['click_value']
                self.passive_income = data['passive_income']
                self.stats = data['stats']
                
                # Load upgrades
                for (name, count, cost), upgrade in zip(data['upgrades'], self.upgrades):
                    upgrade.count = count
                    upgrade.cost = cost
        except FileNotFoundError:
            pass  # No save file exists yet

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
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
            
            self.update()
            self.draw()
            clock.tick(60)
        
        # Save game before quitting
        self.save_game()
        pygame.quit()
        sys.exit()
