# game.py
import pygame
import sys
import os
from pygame import mixer
import random
import math
from typing import List, Dict
import json
from models import Upgrade
from game_data import PROMOTION_LEVELS, CLICK_MESSAGES
from story_events import initialize_story_events, StoryEvent
from achievements import ACHIEVEMENTS, Achievement

class BusinessClicker:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Configuration de l'écran
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.width = self.screen.get_width()
        self.height = self.screen.get_height()
        pygame.display.set_caption("Business Clicker")
        
        # État du jeu
        self.money = 0
        self.click_value = 1
        self.passive_income = 0
        self.last_passive_update = pygame.time.get_ticks()
        self.score_multiplier = 1.0
        self.combo_counter = 0
        self.last_click_time = 0
        self.combo_timeout = 2000  # 2 secondes pour maintenir le combo
        
        # Configuration de l'interface
        self.font_large = pygame.font.Font(None, 64)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # Initialisation des systèmes de jeu
        self.upgrades = self.initialize_upgrades()
        self.story_events = initialize_story_events()
        self.achievements = ACHIEVEMENTS
        self.promotion_levels = PROMOTION_LEVELS
        self.click_messages = CLICK_MESSAGES
        self.selected_upgrade = None
        self.current_position = "Stagiaire"
        
        # États et queues
        self.active_events = []
        self.messages_queue = []
        
        # Chargement des ressources et configuration UI
        self.load_assets()
        self.setup_ui()
        
        # Animation et particules
        self.click_animation = False
        self.animation_frame = 0
        self.animation_max_frame = 10
        self.particles = []
        
        # Statistiques
        self.stats = {
            'total_clicks': 0,
            'total_money_earned': 0,
            'total_upgrades_bought': 0
        }
        
        # Charger la partie sauvegardée
        self.load_game()

    def initialize_upgrades(self) -> List[Upgrade]:
        return [
            Upgrade("Machine à Café", 10, 0.1, "Un petit café pour la productivité"),
            Upgrade("Stagiaire", 50, 0.5, "Il fait de son mieux..."),
            Upgrade("Ordinateur de Bureau", 200, 2, "Traitement des dossiers plus rapide"),
            Upgrade("Scanner Automatique", 1000, 10, "Scanne les documents tout seul"),
            Upgrade("Assistant IA", 5000, 50, "Productivité nouvelle génération")
        ]

    def load_assets(self):
        self.background = pygame.image.load(os.path.join('assets', 'images', 'office_background.png'))
        self.background = pygame.transform.scale(self.background, (self.width, self.height))
        
        document_size = int(self.height * 0.15)
        original_document = pygame.image.load(os.path.join('assets', 'images', 'document_pixel.png'))
        self.document = pygame.transform.scale(original_document, (document_size, document_size))
        self.document_rect = self.document.get_rect(center=(self.width // 2, self.height // 2))
        
        self.click_sound = mixer.Sound(os.path.join('assets', 'sounds', 'paper_shuffle.wav'))
        self.click_sound.set_volume(0.2)
        
        self.upgrade_icons = {}
        for upgrade in self.upgrades:
            icon_path = os.path.join('assets', 'images', f'{upgrade.name.lower().replace(" ", "_")}.png')
            if os.path.exists(icon_path):
                self.upgrade_icons[upgrade.name] = pygame.image.load(icon_path)
            else:
                icon = pygame.Surface((32, 32))
                icon.fill((random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)))
                self.upgrade_icons[upgrade.name] = icon

    def setup_ui(self):
        self.upgrade_region = pygame.Rect(self.width - 400, 0, 400, self.height)  # Largeur augmentée à 400
        self.stats_region = pygame.Rect(0, 0, 300, 100)
        
        self.upgrade_buttons = []
        for i, upgrade in enumerate(self.upgrades):
            button_rect = pygame.Rect(
                self.upgrade_region.x + 10,
                100 + i * 90,
                380,
                80
            )
            self.upgrade_buttons.append((button_rect, upgrade))


    def check_promotion(self):
        # On cherche le plus haut poste débloqué au lieu de prendre le premier qui dépasse
        highest_position = self.current_position
        for position, threshold in sorted(self.promotion_levels.items(), key=lambda x: x[1]):
            if self.money >= threshold:
                highest_position = position
                
        if highest_position != self.current_position:
            self.current_position = highest_position
            self.add_message(
                f"Promotion !",
                f"Félicitations ! Vous êtes promu {highest_position}. Nouveaux avantages débloqués !"
            )
            return True
        return False


    def add_message(self, title, description, duration=5000, priority='normal'):
        current_time = pygame.time.get_ticks()
        
        if priority == 'story':
            duration = 10000
        elif priority == 'random':
            duration = 3000
            for msg in self.messages_queue:
                if msg['priority'] == 'random' and \
                   current_time - msg['creation_time'] < msg['duration']:
                    return

        for msg in self.messages_queue:
            if msg['title'] == title and msg['description'] == description:
                return
                
        new_message = {
            'title': title,
            'description': description,
            'creation_time': current_time,
            'duration': duration,
            'priority': priority
        }
        
        if priority == 'story':
            self.messages_queue.append(new_message)
        elif priority == 'random':
            self.messages_queue = [msg for msg in self.messages_queue 
                                 if msg['priority'] != 'random']
            self.messages_queue.append(new_message)
            
        if len(self.messages_queue) > 5:
            story_messages = [msg for msg in self.messages_queue 
                            if msg['priority'] == 'story']
            other_messages = [msg for msg in self.messages_queue 
                            if msg['priority'] != 'story']
            
            while len(story_messages) + len(other_messages) > 5:
                if other_messages:
                    other_messages.pop(0)
                elif story_messages:
                    story_messages.pop(0)
                    
            self.messages_queue = story_messages + other_messages

    def update_messages(self):
        current_time = pygame.time.get_ticks()
        self.messages_queue = [msg for msg in self.messages_queue 
                             if current_time - msg['creation_time'] < msg['duration']]

    def check_story_events(self):
        for event in self.story_events:
            if not event.triggered:
                if event.event_type == 'money' and self.money >= event.trigger_value:
                    event.triggered = True
                    self.add_message(event.title, event.description, priority='story')
                elif event.event_type == 'clicks' and self.stats['total_clicks'] >= event.trigger_value:
                    event.triggered = True
                    self.add_message(event.title, event.description, priority='story')
                elif event.event_type == 'upgrades' and self.stats['total_upgrades_bought'] >= event.trigger_value:
                    event.triggered = True
                    self.add_message(event.title, event.description, priority='story')

    def check_achievements(self):
        for achievement in self.achievements:
            if not achievement.unlocked:
                if achievement.condition_type == "clicks" and self.stats['total_clicks'] >= achievement.condition_value:
                    self.unlock_achievement(achievement)
                elif achievement.condition_type == "upgrades" and self.stats['total_upgrades_bought'] >= achievement.condition_value:
                    self.unlock_achievement(achievement)
                elif achievement.condition_type == "money_earned" and self.stats['total_money_earned'] >= achievement.condition_value:
                    self.unlock_achievement(achievement)

    def unlock_achievement(self, achievement):
        achievement.unlocked = True
        self.money += achievement.reward
        self.add_message(
            f"Achievement débloqué : {achievement.title}",
            f"{achievement.description}\nRécompense : {achievement.reward}€",
            priority='achievement'
        )

    def create_particles(self, pos, count=5):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 5)
            lifetime = random.randint(20, 40)
            gain_text = f"+{self.click_value * self.score_multiplier:.1f}€"
            self.particles.append({
                'pos': list(pos),
                'vel': [math.cos(angle) * speed, math.sin(angle) * speed],
                'lifetime': lifetime,
                'max_lifetime': lifetime,
                'text': gain_text
            })

    def update_particles(self):
        for particle in self.particles[:]:
            particle['pos'][0] += particle['vel'][0]
            particle['pos'][1] += particle['vel'][1]
            particle['lifetime'] -= 1
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)

    def handle_click(self, pos):
        if self.document_rect.collidepoint(pos):
            current_time = pygame.time.get_ticks()
            if current_time - self.last_click_time < self.combo_timeout:
                self.combo_counter += 1
                self.score_multiplier = min(2.0, 1 + (self.combo_counter * 0.1))
            else:
                self.combo_counter = 0
                self.score_multiplier = 1.0
                
            self.last_click_time = current_time
            
            gain = self.click_value * self.score_multiplier
            self.money += gain
            self.stats['total_clicks'] += 1
            self.stats['total_money_earned'] += gain
            
            self.click_animation = True
            self.animation_frame = 0
            self.create_particles(pos)
            
            channel = mixer.find_channel(True)
            if channel:
                channel.play(self.click_sound, maxtime=500)
            
            if random.random() < 0.05:
                self.add_message("", random.choice(self.click_messages), priority='random')
        
        for button, upgrade in self.upgrade_buttons:
            if button.collidepoint(pos):
                self.try_purchase_upgrade(upgrade)

    def try_purchase_upgrade(self, upgrade):
        if self.money >= upgrade.cost:
            self.money -= upgrade.cost
            upgrade.count += 1
            self.passive_income += upgrade.productivity_boost
            self.stats['total_upgrades_bought'] += 1
            
            upgrade.cost = int(upgrade.cost * 1.15)

    def update(self):
        current_time = pygame.time.get_ticks()
        
        time_diff = (current_time - self.last_passive_update) / 1000.0
        earned = self.passive_income * time_diff
        self.money += earned
        self.stats['total_money_earned'] += earned
        self.last_passive_update = current_time
        
        self.update_animation()
        self.update_particles()
        self.check_story_events()
        self.check_promotion()
        self.check_achievements()
        self.update_messages()

    def update_animation(self):
        if self.click_animation:
            self.animation_frame += 1
            if self.animation_frame >= self.animation_max_frame:
                self.click_animation = False
                self.animation_frame = 0
                return

            if self.animation_frame < self.animation_max_frame / 2:
                scale = 0.9
            else:
                scale = 1.0
                
            original_size = self.document.get_rect().size
            scaled_size = (int(original_size[0] * scale), int(original_size[1] * scale))
            scaled_doc = pygame.transform.scale(self.document, scaled_size)
            
            old_center = self.document_rect.center
            self.document_rect = scaled_doc.get_rect(center=old_center)

    def draw_messages(self):
        if not self.messages_queue:
            return

        msg = self.messages_queue[-1]
        margin = 20
        padding = 10
        max_width = 800
        
        def wrap_text(text, font, max_width):
            words = text.split(' ')
            lines = []
            current_line = []
            current_width = 0
            
            for word in words:
                word_surface = font.render(word + ' ', True, (0, 0, 0))
                word_width = word_surface.get_width()
                
                if current_width + word_width <= max_width:
                    current_line.append(word)
                    current_width += word_width
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                    current_width = word_width
            
            if current_line:
                lines.append(' '.join(current_line))
            
            return lines
        
        title_height = self.font_medium.get_linesize() if msg['title'] else 0
        desc_lines = wrap_text(msg['description'], self.font_small, max_width - 2 * padding)
        desc_height = len(desc_lines) * self.font_small.get_linesize()
        
        total_height = padding * 2 + title_height + desc_height
        msg_surface = pygame.Surface((max_width, total_height))
        msg_surface.fill((240, 240, 240))
        msg_rect = msg_surface.get_rect(midbottom=(self.width // 2, self.height - margin))
        
        elapsed = pygame.time.get_ticks() - msg['creation_time']
        alpha = max(0, min(255, int(255 * (1 - elapsed / msg['duration']))))
        msg_surface.set_alpha(alpha)
        
        if msg['priority'] == 'story':
            border_color = (100, 150, 255)
            title_color = (0, 0, 150)
        elif msg['priority'] == 'achievement':
            border_color = (255, 215, 0)  # Or pour les achievements
            title_color = (184, 134, 11)
        else:
            border_color = (200, 200, 200)
            title_color = (0, 0, 0)
        
        current_y = padding
        
        if msg['title']:
            title_text = self.font_medium.render(msg['title'], True, title_color)
            msg_surface.blit(title_text, (padding, current_y))
            current_y += title_height + 5
        
        for line in desc_lines:
            line_text = self.font_small.render(line, True, (50, 50, 50))
            msg_surface.blit(line_text, (padding, current_y))
            current_y += self.font_small.get_linesize()
        
        pygame.draw.rect(msg_surface, border_color, msg_surface.get_rect(), 2)
        self.screen.blit(msg_surface, msg_rect)

    def draw_upgrade_panel(self):
        pygame.draw.rect(self.screen, (240, 240, 240), self.upgrade_region)
        
        title_text = self.font_medium.render("Améliorations", True, (0, 0, 0))
        self.screen.blit(title_text, (self.upgrade_region.x + 10, 50))
        
        for button, upgrade in self.upgrade_buttons:
            # Couleur de fond en fonction de la possibilité d'achat
            color = (200, 200, 200) if self.money >= upgrade.cost else (150, 150, 150)
            pygame.draw.rect(self.screen, color, button, border_radius=5)
            
            # Icône
            icon = self.upgrade_icons[upgrade.name]
            icon_rect = icon.get_rect(midleft=(button.x + 10, button.centery))
            self.screen.blit(icon, icon_rect)
            
            # Textes
            name_text = self.font_medium.render(upgrade.name, True, (0, 0, 0))  # Police plus grande
            cost_text = self.font_small.render(f"Coût : {upgrade.cost}€", True, (0, 0, 0))
            count_text = self.font_small.render(f"Niveau : {upgrade.count}", True, (0, 0, 0))
            productivity_text = self.font_small.render(
                f"+{upgrade.productivity_boost:.1f}€/s",
                True,
                (0, 100, 0)
            )
            
            # Positionnement des textes avec plus d'espace
            self.screen.blit(name_text, (button.x + 50, button.y + 10))
            self.screen.blit(cost_text, (button.x + 50, button.y + 35))
            self.screen.blit(productivity_text, (button.x + 50, button.y + 55))
            self.screen.blit(count_text, (button.right - 100, button.centery))

    def draw_stats(self):
        pygame.draw.rect(self.screen, (240, 240, 240), self.stats_region)
        
        money_text = self.font_large.render(f"{int(self.money)}€", True, (0, 0, 0))
        self.screen.blit(money_text, (20, 20))
        
        income_text = self.font_medium.render(f"{self.passive_income:.1f}€/s", True, (0, 100, 0))
        self.screen.blit(income_text, (20, 70))

        if self.score_multiplier > 1.0:
            combo_color = (255, 165, 0)
            if self.score_multiplier >= 1.5:
                combo_color = (255, 69, 0)  # Orange plus foncé pour les gros combos
                
            multiplier_text = self.font_medium.render(
                f"Combo x{self.score_multiplier:.1f}",
                True,
                combo_color
            )
            self.screen.blit(multiplier_text, (20, 120))

        position_text = self.font_medium.render(f"Poste : {self.current_position}", True, (0, 0, 0))
        self.screen.blit(position_text, (20, 160))

        # Statistiques en bas de l'écran
        stats_y = self.height - 100
        clicks_text = self.font_small.render(f"Clics totaux : {self.stats['total_clicks']}", True, (0, 0, 0))
        money_earned_text = self.font_small.render(
            f"Argent total gagné : {int(self.stats['total_money_earned'])}€",
            True,
            (0, 0, 0)
        )
        upgrades_text = self.font_small.render(
            f"Améliorations achetées : {self.stats['total_upgrades_bought']}",
            True,
            (0, 0, 0)
        )
        
        self.screen.blit(clicks_text, (20, stats_y))
        self.screen.blit(money_earned_text, (20, stats_y + 25))
        self.screen.blit(upgrades_text, (20, stats_y + 50))

    def draw_particles(self):
        for particle in self.particles:
            alpha = int(255 * (particle['lifetime'] / particle['max_lifetime']))
            text_color = (0, 200, 0) if self.score_multiplier == 1.0 else (255, 165, 0)
            text = self.font_small.render(particle['text'], True, text_color)
            text.set_alpha(alpha)
            self.screen.blit(text, particle['pos'])

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.document, self.document_rect)
        self.draw_upgrade_panel()
        self.draw_stats()
        self.draw_particles()
        self.draw_messages()
        pygame.display.flip()

    def save_game(self):
        save_data = {
            'money': self.money,
            'click_value': self.click_value,
            'passive_income': self.passive_income,
            'stats': self.stats,
            'upgrades': [(u.name, u.count, u.cost) for u in self.upgrades],
            'current_position': self.current_position,
            'triggered_events': [event.triggered for event in self.story_events],
            'achievements': [(a.title, a.unlocked) for a in self.achievements]
        }
        with open('sauvegarde.json', 'w') as f:
            json.dump(save_data, f)

    def load_game(self):
        try:
            with open('sauvegarde.json', 'r') as f:
                data = json.load(f)

                self.money = data['money']
                self.click_value = data['click_value']
                self.passive_income = data['passive_income']
                self.stats = data['stats']
                self.current_position = data.get('current_position', "Stagiaire")

                # Charger les événements déclenchés
                for event, triggered in zip(self.story_events, data.get('triggered_events', [])):
                    event.triggered = triggered

                # Charger les améliorations
                for (name, count, cost), upgrade in zip(data['upgrades'], self.upgrades):
                    upgrade.count = count
                    upgrade.cost = cost

                # Charger les achievements
                for (title, unlocked), achievement in zip(data.get('achievements', []), self.achievements):
                    achievement.unlocked = unlocked

        except FileNotFoundError:
            pass  # Pas de sauvegarde existante

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
            
            self.update()
            self.draw()
            clock.tick(60)
        
        # Sauvegarder avant de quitter
        self.save_game()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = BusinessClicker()
    game.run()