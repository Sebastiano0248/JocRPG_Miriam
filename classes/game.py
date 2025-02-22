import pygame
import sys
from classes.character import Character
from classes.room import Room

class Game:
    def __init__(self):
        pygame.init()
        self.width, self.height = 720, 640
        self.window = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Miriam')
        self.character = Character('data\\textures\\sprites\\mirom.gif', 550, 400)
        self.room = Room.load_from_json('data\\rooms.json', 'Habitasao')
        self.state = 0
        self.room.set_background(self.state)
        self.space_pressed = False
        self.showing_text = False
        self.immobilized = False
        self.showing_image = None
        self.current_text = ""
        self.text_index = 0
        self.text_speed = 30
        self.last_text_update = pygame.time.get_ticks()
        self.text_start_time = 0
        self.text_display_duration = 5000
        self.font = pygame.font.Font("data\\fonts\\Ticketing.ttf", 24)
        self.text_bubble = pygame.image.load("data\\textures\\textboxes\\Bombolla_text.png")
        self.running = True
        self.showing_code_input = False
        self.input_code = ""
        self.correct_code = ""
        self.correct_image = None
        self.correct_next_state = None
        self.code_prompt = ""
        self.correct_image_path = ""

    def wrap_text(self, text, max_length):
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            if len(current_line) + len(word) + 1 <= max_length:
                current_line += (" " if current_line else "") + word
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            print(self.state)
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.showing_code_input or self.showing_image:
                    if event.key == pygame.K_RETURN:
                        print(self.input_code + " " + self.correct_code)
                        if self.input_code == self.correct_code:
                            if self.correct_image:
                                self.showing_image = pygame.transform.scale(self.correct_image, (self.width - 100, self.height - 100))
                            else:
                                self.showing_text = True
                                self.current_text = self.correct_image_path
                                self.text_index = 0
                                self.text_start_time = pygame.time.get_ticks()
                            self.immobilized = True
                            self.state = self.correct_next_state
                            self.room.set_background(self.state)
                        else:
                            self.immobilized = False
                        self.showing_code_input = False
                        self.input_code = ""
                    elif event.key == pygame.K_SPACE and self.showing_image:
                        self.showing_image = None
                        self.immobilized = False
                        self.space_pressed = True
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_code = self.input_code[:-1]
                    else:
                        self.input_code += event.unicode
                elif self.showing_text and event.key == pygame.K_SPACE:
                    self.showing_text = False
                    self.immobilized = False
                    self.space_pressed = True

    def update(self):
        keys = pygame.key.get_pressed()
        self.character.update(keys, self.width, self.height, self.room.invisible_rects, self.immobilized)
        character_rect = self.character.get_rect()

        if not self.space_pressed and not self.showing_code_input and not self.showing_image and not self.showing_text:
            for square in self.room.blue_squares:
                if not (self.state in square["states"]) and keys[pygame.K_SPACE] and character_rect.colliderect(square["rect"]):
                    self.room = Room.load_from_json('data\\rooms.json', square["target_room"])
                    self.room.set_background(self.state)
                    self.character.move(*square["spawn_coords"])
                    if square["next_state"] is not None:
                        self.state = square["next_state"]
                        self.room.set_background(self.state)
                    break
            else:
                for square in self.room.yellow_squares:
                    if not (self.state in square["states"]) and not self.showing_image and keys[pygame.K_SPACE] and not self.space_pressed and character_rect.colliderect(square["rect"]):
                        self.showing_image = pygame.transform.scale(square["image"], (self.width - 100, self.height - 100))
                        self.immobilized = True
                        if square["next_state"] is not None:
                            self.state = square["next_state"]
                            self.room.set_background(self.state)
                        break
                    elif keys[pygame.K_SPACE] and self.showing_image:
                        self.showing_image = None
                        self.immobilized = False
                        break
                else:
                    for square in self.room.red_squares:
                        if not (self.state in square["states"]) and keys[pygame.K_SPACE] and character_rect.colliderect(square["rect"]):
                            self.showing_code_input = True
                            self.correct_code = square["code"]
                            print(self.correct_code)
                            self.correct_image = square["image"]
                            self.correct_image_path = square["image_path"]
                            self.correct_next_state = square["next_state"] if square["next_state"] else self.state
                            self.code_prompt = square["code_prompt"]
                            self.immobilized = True
                            break
                    else:
                        for square in self.room.green_squares:
                            if not (self.state in square["states"]) and keys[pygame.K_SPACE] and character_rect.colliderect(square["rect"]):
                                self.showing_text = True
                                self.current_text = square["text"]
                                self.text_index = 0
                                self.text_start_time = pygame.time.get_ticks()
                                self.immobilized = True
                                if square["next_state"] is not None:
                                    self.state = square["next_state"]
                                    self.room.set_background(self.state)
                                break

        self.space_pressed = keys[pygame.K_SPACE]

    def draw(self):
        self.room.draw(self.window)
        self.character.draw(self.window)
        if self.showing_text:
            self.window.blit(self.text_bubble, (30, 30))
            current_time = pygame.time.get_ticks()
            if current_time - self.last_text_update > self.text_speed and self.text_index < len(self.current_text):
                self.text_index += 1
                self.last_text_update = current_time
            lines = self.wrap_text(self.current_text[:self.text_index], 55)
            y_offset = 50
            for line in lines:
                text_surface = self.font.render(line, True, (0, 0, 0))  # Change text color to black
                self.window.blit(text_surface, (50, y_offset))
                y_offset += 30
        if self.showing_image:
            img_rect = self.showing_image.get_rect(center=(self.width // 2, self.height // 2))
            self.window.blit(self.showing_image, img_rect.topleft)
        if self.showing_code_input:
            self.window.blit(self.text_bubble, (30, 30))
            code_surface = self.font.render(f"{self.code_prompt} {self.input_code}", True, (0, 0, 0))
            self.window.blit(code_surface, (50, 50))
        pygame.display.flip()
