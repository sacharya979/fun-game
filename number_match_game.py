import pygame
import random
import sys
import os
import json
from pygame import mixer

# Initialize Pygame and mixer
pygame.init()
mixer.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
CARD_SIZE = 100
CARD_MARGIN = 20
FONT_SIZE = 48
TITLE_FONT_SIZE = 64
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50

# Colors
BACKGROUND_COLOR = (230, 230, 250)  # Light lavender
CARD_COLOR = (255, 182, 193)    # Light pink
MATCHED_COLOR = (152, 251, 152)  # Light green
TEXT_COLOR = (70, 70, 70)       # Dark grey
SCORE_COLOR = (106, 90, 205)    # Slate blue
BUTTON_COLOR = (176, 224, 230)  # Powder blue
BUTTON_HOVER_COLOR = (137, 207, 240)  # Baby blue

# Set up the display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Fun Number Match!")

# Fonts
font = pygame.font.Font(None, FONT_SIZE)
title_font = pygame.font.Font(None, TITLE_FONT_SIZE)

# Game sounds
try:
    correct_sound = pygame.mixer.Sound("sounds/correct.wav")
    wrong_sound = pygame.mixer.Sound("sounds/wrong.wav")
    win_sound = pygame.mixer.Sound("sounds/win.wav")
    click_sound = pygame.mixer.Sound("sounds/click.wav")
    pygame.mixer.music.load("sounds/background_music.wav")
    pygame.mixer.music.set_volume(0.3)
except:
    # If sound files don't exist, create silent sounds
    correct_sound = wrong_sound = win_sound = click_sound = pygame.mixer.Sound(buffer=bytearray([0]))

# Game states
MENU = "menu"
PLAYING = "playing"
GAME_OVER = "game_over"

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.hovered = False

    def draw(self):
        color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, TEXT_COLOR, self.rect, 3, border_radius=10)
        
        text_surface = font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            click_sound.play()
            return True
        return False

class Card:
    def __init__(self, x, y, number, is_arithmetic=False):
        self.rect = pygame.Rect(x, y, CARD_SIZE, CARD_SIZE)
        self.number = number
        self.revealed = False
        self.matched = False
        self.hover = False
        self.is_arithmetic = is_arithmetic
        self.animation_scale = 1.0
        self.target_scale = 1.0

    def draw(self):
        # Animation scaling
        current_size = int(CARD_SIZE * self.animation_scale)
        current_rect = pygame.Rect(
            self.rect.centerx - current_size // 2,
            self.rect.centery - current_size // 2,
            current_size,
            current_size
        )

        # Draw card shadow when hovering
        if self.hover and not self.matched:
            shadow_rect = current_rect.copy()
            shadow_rect.x += 5
            shadow_rect.y += 5
            pygame.draw.rect(screen, (180, 180, 180), shadow_rect, border_radius=15)

        color = MATCHED_COLOR if self.matched else CARD_COLOR
        pygame.draw.rect(screen, color, current_rect, border_radius=15)
        pygame.draw.rect(screen, TEXT_COLOR, current_rect, 3, border_radius=15)
        
        if self.revealed or self.matched:
            if isinstance(self.number, tuple):
                # For arithmetic mode
                text = f"{self.number[0]} {self.number[1]} {self.number[2]}"
            else:
                text = str(self.number)
            text_surface = font.render(text, True, TEXT_COLOR)
            text_rect = text_surface.get_rect(center=current_rect.center)
            screen.blit(text_surface, text_rect)

        # Update animation
        if self.animation_scale != self.target_scale:
            self.animation_scale += (self.target_scale - self.animation_scale) * 0.2

    def animate_reveal(self):
        self.target_scale = 1.1

    def animate_hide(self):
        self.target_scale = 1.0

class Game:
    def __init__(self):
        self.state = MENU
        self.load_high_scores()
        self.difficulty = "easy"
        self.mode = "numbers"
        self.setup_menu()
        pygame.mixer.music.play(-1)

    def load_high_scores(self):
        try:
            with open("high_scores.json", "r") as f:
                self.high_scores = json.load(f)
        except:
            self.high_scores = {"easy": 0, "medium": 0, "hard": 0}

    def save_high_scores(self):
        with open("high_scores.json", "w") as f:
            json.dump(self.high_scores, f)

    def setup_menu(self):
        center_x = WINDOW_WIDTH // 2 - BUTTON_WIDTH // 2
        self.menu_buttons = [
            Button(center_x, 200, BUTTON_WIDTH, BUTTON_HEIGHT, "Easy Mode"),
            Button(center_x, 270, BUTTON_WIDTH, BUTTON_HEIGHT, "Medium Mode"),
            Button(center_x, 340, BUTTON_WIDTH, BUTTON_HEIGHT, "Hard Mode"),
            Button(center_x, 410, BUTTON_WIDTH, BUTTON_HEIGHT, "Arithmetic Mode")
        ]

    def create_arithmetic_cards(self):
        operations = ["+", "-", "×"]
        cards = []
        used_pairs = set()

        while len(cards) < self.get_pair_count() * 2:
            a = random.randint(1, 10)
            b = random.randint(1, 10)
            op = random.choice(operations)
            
            if op == "+":
                result = a + b
            elif op == "-":
                if a < b:  # Ensure positive results
                    a, b = b, a
                result = a - b
            else:  # multiplication
                result = a * b

            if (a, op, b) not in used_pairs and result <= 20:
                cards.append((a, op, b))
                cards.append(result)
                used_pairs.add((a, op, b))

        random.shuffle(cards)
        return cards

    def get_pair_count(self):
        if self.difficulty == "easy":
            return 5
        elif self.difficulty == "medium":
            return 8
        else:
            return 12

    def create_board(self):
        if self.mode == "arithmetic":
            numbers = self.create_arithmetic_cards()
        else:
            pair_count = self.get_pair_count()
            numbers = list(range(1, pair_count + 1)) * 2
            random.shuffle(numbers)

        cards = []
        cols = 5 if pair_count <= 8 else 6
        rows = (len(numbers) + cols - 1) // cols

        card_width = min(CARD_SIZE, (WINDOW_WIDTH - (cols + 1) * CARD_MARGIN) // cols)
        card_height = min(CARD_SIZE, (WINDOW_HEIGHT - 200 - (rows + 1) * CARD_MARGIN) // rows)
        card_size = min(card_width, card_height)

        x_start = (WINDOW_WIDTH - (cols * (card_size + CARD_MARGIN))) // 2
        y_start = (WINDOW_HEIGHT - (rows * (card_size + CARD_MARGIN))) // 2

        index = 0
        for row in range(rows):
            for col in range(cols):
                if index < len(numbers):
                    x = x_start + col * (card_size + CARD_MARGIN)
                    y = y_start + row * (card_size + CARD_MARGIN)
                    cards.append(Card(x, y, numbers[index], self.mode == "arithmetic"))
                    index += 1

        return cards

    def run(self):
        self.cards = self.create_board()
        self.first_card = None
        self.matched_pairs = 0
        self.attempts = 0
        self.game_won = False

        while True:
            if self.state == MENU:
                self.run_menu()
            elif self.state == PLAYING:
                self.run_game()
            elif self.state == GAME_OVER:
                self.run_game_over()

    def run_menu(self):
        screen.fill(BACKGROUND_COLOR)
        
        # Draw title
        title = title_font.render("Fun Number Match!", True, TEXT_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, 100))
        screen.blit(title, title_rect)

        # Draw buttons
        for button in self.menu_buttons:
            button.draw()

        # Draw high scores
        y = 480
        for diff in ["easy", "medium", "hard"]:
            score_text = font.render(f"{diff.title()}: {self.high_scores[diff]}", True, SCORE_COLOR)
            score_rect = score_text.get_rect(center=(WINDOW_WIDTH//2, y))
            screen.blit(score_text, score_rect)
            y += 40

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            for i, button in enumerate(self.menu_buttons):
                if button.handle_event(event):
                    if i == 0:
                        self.difficulty = "easy"
                        self.mode = "numbers"
                    elif i == 1:
                        self.difficulty = "medium"
                        self.mode = "numbers"
                    elif i == 2:
                        self.difficulty = "hard"
                        self.mode = "numbers"
                    else:
                        self.difficulty = "medium"
                        self.mode = "arithmetic"
                    self.state = PLAYING
                    self.cards = self.create_board()
                    return

    def run_game(self):
        screen.fill(BACKGROUND_COLOR)
        
        # Draw title
        title = title_font.render("Fun Number Match!", True, TEXT_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, 50))
        screen.blit(title, title_rect)
        
        # Draw score
        score_text = font.render(f"Matches: {self.matched_pairs}/{self.get_pair_count()}    Tries: {self.attempts}", True, SCORE_COLOR)
        screen.blit(score_text, (20, 20))
        
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN and not self.game_won:
                for card in self.cards:
                    if card.rect.collidepoint(mouse_pos) and not card.revealed and not card.matched:
                        card.revealed = True
                        card.animate_reveal()
                        
                        if self.first_card is None:
                            self.first_card = card
                        else:
                            self.attempts += 1
                            # Check if cards match
                            match = False
                            if self.mode == "arithmetic":
                                if isinstance(self.first_card.number, tuple):
                                    # Calculate arithmetic result
                                    a, op, b = self.first_card.number
                                    if op == "+":
                                        result = a + b
                                    elif op == "-":
                                        result = a - b
                                    else:  # multiplication
                                        result = a * b
                                    match = result == card.number
                                else:
                                    a, op, b = card.number
                                    if op == "+":
                                        result = a + b
                                    elif op == "-":
                                        result = a - b
                                    else:  # multiplication
                                        result = a * b
                                    match = result == self.first_card.number
                            else:
                                match = self.first_card.number == card.number

                            if match:
                                correct_sound.play()
                                self.first_card.matched = True
                                card.matched = True
                                self.matched_pairs += 1
                                if self.matched_pairs == self.get_pair_count():
                                    self.game_won = True
                                    win_sound.play()
                                    # Update high score
                                    current_score = self.attempts
                                    if self.high_scores[self.difficulty] == 0 or current_score < self.high_scores[self.difficulty]:
                                        self.high_scores[self.difficulty] = current_score
                                        self.save_high_scores()
                            else:
                                wrong_sound.play()
                                # Cards don't match, hide them after a short delay
                                pygame.display.flip()
                                pygame.time.wait(1000)
                                self.first_card.revealed = False
                                card.revealed = False
                                self.first_card.animate_hide()
                                card.animate_hide()
                            self.first_card = None
        
        # Update card hover states
        for card in self.cards:
            card.hover = card.rect.collidepoint(mouse_pos) and not card.matched and not card.revealed
        
        # Draw all cards
        for card in self.cards:
            card.draw()
        
        # Show victory message
        if self.game_won:
            victory_text = title_font.render("You Won! Well Done!", True, SCORE_COLOR)
            text_rect = victory_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 100))
            screen.blit(victory_text, text_rect)
            
            # Show star rating based on attempts and difficulty
            max_attempts = {"easy": 7, "medium": 12, "hard": 20}
            threshold = max_attempts[self.difficulty]
            stars = "★ " * (5 if self.attempts <= threshold else 
                           (4 if self.attempts <= threshold * 1.5 else 
                            (3 if self.attempts <= threshold * 2 else 2)))
            star_text = title_font.render(stars, True, (255, 215, 0))  # Gold color
            star_rect = star_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 50))
            screen.blit(star_text, star_rect)

            # Draw return to menu button
            menu_button = Button(WINDOW_WIDTH//2 - BUTTON_WIDTH//2, WINDOW_HEIGHT - 150, 
                               BUTTON_WIDTH, BUTTON_HEIGHT, "Return to Menu")
            menu_button.draw()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if menu_button.handle_event(event):
                    self.state = MENU
                    return
            
        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()