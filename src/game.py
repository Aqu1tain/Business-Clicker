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

class StoryEvent:
    def __init__(self, title, description, trigger_value, event_type='money'):
        self.title = title
        self.description = description
        self.trigger_value = trigger_value
        self.event_type = event_type  # 'money', 'clicks', 'upgrades'
        self.triggered = False
        self.display_time = None
        self.display_duration = 5000  # 5 secondes

class BusinessClicker:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Configuration de l'écran
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.width = self.screen.get_width()
        self.height = self.screen.get_height()
        pygame.display.set_caption("Business Clicker - Edition Française")
        
        # État du jeu
        self.money = 0
        self.click_value = 1
        self.passive_income = 0
        self.last_passive_update = pygame.time.get_ticks()
        
        # Configuration de l'interface
        self.font_large = pygame.font.Font(None, 64)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # Initialisation des améliorations
        self.upgrades = self.initialize_upgrades()
        self.selected_upgrade = None
        
        # Chargement des ressources
        self.load_assets()
        self.setup_ui()
        
        # État des animations
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

        self.story_events = self.initialize_story_events()
        self.active_events = []
        self.messages_queue = []
        self.current_position = "Stagiaire"
        self.promotion_levels = {
            "Stagiaire": 0,
            "Assistant": 100,
            "Chargé de Mission": 500,
            "Chef de Projet": 2000,
            "Directeur Adjoint": 5000,
            "Directeur": 10000,
            "PDG": 50000
        }


        self.click_messages = [
            "Encore un dossier de traité !",
            "La machine est bien huilée",
            "Un de plus pour la boîte",
            "Le patron va être content",
            "Ça sent la promotion",
            "La routine, quoi",
            "Pas mal du tout",
            "C'est du bon boulot",
        ]
        
        # Charger la partie sauvegardée si elle existe
        self.load_game()
        
    def initialize_upgrades(self) -> List[Upgrade]:
        return [
            Upgrade("Machine à Café", 10, 0.1, "Un petit café pour la productivité"),
            Upgrade("Stagiaire", 50, 0.5, "Il fait de son mieux..."),
            Upgrade("Ordinateur de Bureau", 200, 2, "Traitement des dossiers plus rapide"),
            Upgrade("Scanner Automatique", 1000, 10, "Scanne les documents tout seul"),
            Upgrade("Assistant IA", 5000, 50, "Productivité nouvelle génération")
        ]

    def initialize_story_events(self):
        return [
            StoryEvent(
                "Premier Jour",
                "Bienvenue dans l'entreprise ! On vous a assigné un bureau avec un ordinateur qui tourne sous Windows 95. Le chef vous rappelle gentiment qu'il faut remplir la feuille de présence tous les matins.",
                0, "money"
            ),
            StoryEvent(
                "Premier Café",
                "Vous découvrez la machine à café. La pause de 10h ne sera plus jamais la même ! Les collègues vous initient au sacro-saint rituel du café-clope-potins.",
                10, "money"
            ),
            StoryEvent(
                "Premier Salaire",
                "Votre premier salaire ! Maintenant vous pouvez vous acheter des sandwichs à la cafétéria. Plus besoin de manger des pâtes tous les midis.",
                100, "money"
            ),
            StoryEvent(
                "La Routine",
                "Vous commencez à maîtriser l'art de paraître occupé pendant les heures creuses. Votre technique de la double fenêtre Excel-Facebook est maintenant au point.",
                50, "clicks"
            ),
            StoryEvent(
                "Expert Excel",
                "Vous savez maintenant faire des tableaux croisés dynamiques. Vos collègues vous regardent différemment. Le stagiaire vous demande même des conseils !",
                200, "clicks"
            ),
            StoryEvent(
                "Première Réunion",
                "Vous êtes invité à une réunion qui aurait pu être un email. Mais vous avez découvert où se cachaient les meilleurs gâteaux de la salle de pause !",
                3, "upgrades"
            ),
            StoryEvent(
                "Maître du Café",
                "Les gens viennent maintenant de l'autre bout du bâtiment pour votre café. Vous êtes une légende vivante de la pause café. Même le DRH vous demande votre secret.",
                5, "upgrades"
            ),
            StoryEvent(
                "Promotion : Assistant",
                "Félicitations ! Vous êtes promu Assistant. Vous avez maintenant accès à la grande imprimante et aux fournitures de bureau premium. Les Post-it de luxe, ça change la vie !",
                100, "money"
            ),
            StoryEvent(
                "Promotion : Chargé de Mission",
                "Vous êtes maintenant Chargé de Mission ! On vous a donné un badge pour la salle de réunion VIP et une place de parking presque couverte. La classe !",
                500, "money"
            )
        ]


    def check_promotion(self):
        for position, threshold in sorted(self.promotion_levels.items(), key=lambda x: x[1]):
            if self.money >= threshold and position != self.current_position:
                self.current_position = position
                self.add_message(
                    f"Promotion !",
                    f"Félicitations ! Vous êtes promu {position}. Nouveaux avantages débloqués !"
                )
                return True
        return False

    def add_message(self, title, description, duration=5000, priority='normal'):
        current_time = pygame.time.get_ticks()
        
        # Définir les durées selon le type de message
        if priority == 'story':
            duration = 10000  # 10 secondes pour les messages d'histoire
        elif priority == 'random':
            duration = 3000   # 3 secondes pour les messages aléatoires
            
            # Vérifier si un message aléatoire est déjà en cours
            for msg in self.messages_queue:
                if msg['priority'] == 'random' and \
                   current_time - msg['creation_time'] < msg['duration']:
                    return  # Ne pas ajouter de nouveau message aléatoire
        
        # Vérifier les doublons
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
        
        # Gérer la priorité dans la queue
        if priority == 'story':
            # Les messages d'histoire sont toujours ajoutés
            self.messages_queue.append(new_message)
        elif priority == 'random':
            # Supprimer les anciens messages aléatoires
            self.messages_queue = [msg for msg in self.messages_queue 
                                 if msg['priority'] != 'random']
            self.messages_queue.append(new_message)
            
        # Limiter la taille de la queue
        if len(self.messages_queue) > 5:
            # Garder les messages d'histoire prioritaires
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

    def load_assets(self):
        # Même code que précédemment pour le chargement des assets
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
        # Création des régions de l'interface
        self.upgrade_region = pygame.Rect(self.width - 300, 0, 300, self.height)
        self.stats_region = pygame.Rect(0, 0, 300, 100)
        
        # Création des boutons pour les améliorations
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
                'text': '+' + str(self.click_value) + '€'  # Ajout du symbole € après le nombre
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
            self.money += self.click_value
            self.stats['total_clicks'] += 1
            self.stats['total_money_earned'] += self.click_value
            
            self.click_animation = True
            self.animation_frame = 0
            self.create_particles(pos)
            
            channel = mixer.find_channel(True)
            if channel:
                channel.play(self.click_sound, maxtime=500)
            
            # Messages aléatoires avec une plus faible probabilité
            if random.random() < 0.05:  # 5% de chance au lieu de 10%
                self.add_message("", random.choice(self.click_messages), priority='random')
        
        for button, upgrade in self.upgrade_buttons:
            if button.collidepoint(pos):
                self.try_purchase_upgrade(upgrade)

                
    def draw_messages(self):
        if not self.messages_queue:
            return

        msg = self.messages_queue[-1]
        margin = 20
        padding = 10
        max_width = 800  # Largeur maximale augmentée
        
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
        
        # Calculer la hauteur nécessaire pour le message
        title_height = self.font_medium.get_linesize() if msg['title'] else 0
        desc_lines = wrap_text(msg['description'], self.font_small, max_width - 2 * padding)
        desc_height = len(desc_lines) * self.font_small.get_linesize()
        
        total_height = padding * 2 + title_height + desc_height
        
        # Créer la surface du message
        msg_surface = pygame.Surface((max_width, total_height))
        msg_surface.fill((240, 240, 240))
        
        # Centrer en bas de l'écran
        msg_rect = msg_surface.get_rect(midbottom=(self.width // 2, self.height - margin))
        
        # Effet de transparence avec une durée différente selon le type de message
        elapsed = pygame.time.get_ticks() - msg['creation_time']
        alpha = max(0, min(255, int(255 * (1 - elapsed / msg['duration']))))
        msg_surface.set_alpha(alpha)
        
        # Style différent selon le type de message
        if msg['priority'] == 'story':
            border_color = (100, 150, 255)  # Bleu pour les messages d'histoire
            title_color = (0, 0, 150)
        else:
            border_color = (200, 200, 200)  # Gris pour les messages normaux
            title_color = (0, 0, 0)
        
        # Dessiner le titre
        current_y = padding
        if msg['title']:
            title_text = self.font_medium.render(msg['title'], True, title_color)
            msg_surface.blit(title_text, (padding, current_y))
            current_y += title_height + 5
        
        # Dessiner chaque ligne de la description
        for line in desc_lines:
            line_text = self.font_small.render(line, True, (50, 50, 50))
            msg_surface.blit(line_text, (padding, current_y))
            current_y += self.font_small.get_linesize()
        
        # Ajouter une bordure avec la couleur appropriée
        pygame.draw.rect(msg_surface, border_color, msg_surface.get_rect(), 2)
        
        # Afficher le message
        self.screen.blit(msg_surface, msg_rect)

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
        
    def draw_upgrade_panel(self):
        # Dessiner le fond du panneau
        pygame.draw.rect(self.screen, (240, 240, 240), self.upgrade_region)
        
        # Titre du panneau
        title_text = self.font_medium.render("Améliorations", True, (0, 0, 0))
        self.screen.blit(title_text, (self.upgrade_region.x + 10, 50))
        
        # Dessiner les améliorations
        for button, upgrade in self.upgrade_buttons:
            # Fond du bouton
            color = (200, 200, 200) if self.money >= upgrade.cost else (150, 150, 150)
            pygame.draw.rect(self.screen, color, button, border_radius=5)
            
            # Icône de l'amélioration
            icon = self.upgrade_icons[upgrade.name]
            icon_rect = icon.get_rect(midleft=(button.x + 10, button.centery))
            self.screen.blit(icon, icon_rect)
            
            # Informations sur l'amélioration
            name_text = self.font_small.render(upgrade.name, True, (0, 0, 0))
            cost_text = self.font_small.render(f"{upgrade.cost}€", True, (0, 0, 0))
            count_text = self.font_small.render(f"x{upgrade.count}", True, (0, 0, 0))
            
            self.screen.blit(name_text, (button.x + 50, button.y + 10))
            self.screen.blit(cost_text, (button.x + 50, button.y + 30))
            self.screen.blit(count_text, (button.right - 50, button.centery))

    def draw_stats(self):
        # Dessiner le fond des stats
        pygame.draw.rect(self.screen, (240, 240, 240), self.stats_region)
        
        # Afficher l'argent
        money_text = self.font_large.render(f"{int(self.money)}€", True, (0, 0, 0))
        self.screen.blit(money_text, (20, 20))
        
        # Afficher le revenu passif
        income_text = self.font_medium.render(f"{self.passive_income:.1f}€/s", True, (0, 100, 0))
        self.screen.blit(income_text, (20, 70))

        # Afficher les statistiques globales en bas de l'écran
        stats_y = self.height - 100
        clicks_text = self.font_small.render(f"Clics totaux : {self.stats['total_clicks']}", True, (0, 0, 0))
        money_earned_text = self.font_small.render(f"Argent total gagné : {int(self.stats['total_money_earned'])}€", True, (0, 0, 0))
        upgrades_text = self.font_small.render(f"Améliorations achetées : {self.stats['total_upgrades_bought']}", True, (0, 0, 0))
        
        self.screen.blit(clicks_text, (20, stats_y))
        self.screen.blit(money_earned_text, (20, stats_y + 25))
        self.screen.blit(upgrades_text, (20, stats_y + 50))

        position_text = self.font_medium.render(f"Poste : {self.current_position}", True, (0, 0, 0))
        self.screen.blit(position_text, (20, 120))

    def draw_particles(self):
        for particle in self.particles:
            alpha = int(255 * (particle['lifetime'] / particle['max_lifetime']))
            text = self.font_small.render(particle['text'], True, (0, 200, 0))
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
            'triggered_events': [event.triggered for event in self.story_events]
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
                for event, triggered in zip(self.story_events, data.get('triggered_events', [])):
                    event.triggered = triggered

                for (name, count, cost), upgrade in zip(data['upgrades'], self.upgrades):
                    upgrade.count = count
                    upgrade.cost = cost
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