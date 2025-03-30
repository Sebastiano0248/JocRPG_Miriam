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
        self.sound_enabled = True  # Variable para rastrear si el sonido está activado
        self.volume = 0.5  # Volumen inicial (50%)
        pygame.mixer.music.set_volume(self.volume)

        # Cargar el sonido de interacción
        self.interaction_sound = pygame.mixer.Sound("data\\sounds\\\\interaction_sound.mp3")

        # Playlist de música
        self.playlist = [
            "data\\sounds\\\\music\\LostAtASleepover.mp3",
            "data\\sounds\\\\music\\WhereWeUsedToPlay.mp3",
            "data\\sounds\\\\music\\PocketMirrorGaze.mp3"
        ]
        self.current_track_index = 0
        self.setup_music()

        # Intro screen variables
        self.intro_message = "Oh, me ha llegado un \nnuevo mensaje de discord"
        self.intro_font = pygame.font.Font("data\\fonts\\Ticketing.ttf", 48)
        self.intro_duration = 3000  # Duration of the intro in milliseconds
        self.fade_duration = 1000  # Duration of the fade-out in milliseconds

    def setup_music(self):
        if self.sound_enabled:
            pygame.mixer.music.load(self.playlist[self.current_track_index])
            pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)
            pygame.mixer.music.play()

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

    def show_intro(self):
        intro_surface = pygame.Surface((self.width, self.height))
        intro_surface.fill((0, 0, 0))
        
        # Split the intro message into two lines
        lines = self.intro_message.split("\n")
        text_surfaces = [self.intro_font.render(line, True, (255, 255, 255)) for line in lines]
        total_height = sum(surface.get_height() for surface in text_surfaces) + 10  # Add spacing between lines

        y_offset = (self.height - total_height) // 2
        for text_surface in text_surfaces:
            text_rect = text_surface.get_rect(center=(self.width // 2, y_offset + text_surface.get_height() // 2))
            intro_surface.blit(text_surface, text_rect)
            y_offset += text_surface.get_height() + 10  # Move to the next line with spacing

        start_time = pygame.time.get_ticks()
        while True:
            elapsed_time = pygame.time.get_ticks() - start_time
            if elapsed_time > self.intro_duration + self.fade_duration:
                break

            alpha = 255
            if elapsed_time > self.intro_duration:
                alpha = max(0, 255 - int(255 * (elapsed_time - self.intro_duration) / self.fade_duration))
            intro_surface.set_alpha(alpha)

            self.window.fill((0, 0, 0))
            self.window.blit(intro_surface, (0, 0))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

    def run(self):
        self.show_intro()  # Show the intro screen before starting the game loop
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
            elif event.type == pygame.USEREVENT + 1:  # Event triggered when a track ends
                self.current_track_index = (self.current_track_index + 1) % len(self.playlist)
                if self.sound_enabled:
                    pygame.mixer.music.load(self.playlist[self.current_track_index])
                    pygame.mixer.music.play()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:  # Tecla para silenciar o activar el sonido
                    self.sound_enabled = not self.sound_enabled
                    if self.sound_enabled:
                        pygame.mixer.music.unpause()
                    else:
                        pygame.mixer.music.pause()
                elif event.key == pygame.K_MINUS:  # Tecla para bajar el volumen
                    self.volume = max(0.0, self.volume - 0.1)  # No bajar de 0%
                    pygame.mixer.music.set_volume(self.volume)
                elif event.key == pygame.K_PLUS:  # Tecla para subir el volumen
                    self.volume = min(1.0, self.volume + 0.1)  # No subir de 100%
                    pygame.mixer.music.set_volume(self.volume)
                elif event.key == pygame.K_p:  # Tecla para pasar a la siguiente canción
                    self.current_track_index = (self.current_track_index + 1) % len(self.playlist)
                    if self.sound_enabled:
                        pygame.mixer.music.load(self.playlist[self.current_track_index])
                        pygame.mixer.music.play()
                elif event.key == pygame.K_ESCAPE:
                    # Salir de cualquier interacción
                    self.showing_code_input = False
                    self.showing_image = None
                    self.showing_text = False
                    self.immobilized = False
                    self.input_code = ""
                elif self.showing_code_input or self.showing_image:
                    if event.key == pygame.K_RETURN:
                        print(self.input_code + " " + self.correct_code)
                        if self.input_code.strip().lower() == self.correct_code.strip().lower():
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
                    # Reproducir sonido de interacción
                    self.interaction_sound.play()
                    break
            else:
                for square in self.room.yellow_squares:
                    if not (self.state in square["states"]) and not self.showing_image and keys[pygame.K_SPACE] and not self.space_pressed and character_rect.colliderect(square["rect"]):
                        self.showing_image = pygame.transform.scale(square["image"], (self.width - 100, self.height - 100))
                        self.immobilized = True
                        if square["next_state"] is not None:
                            self.state = square["next_state"]
                            self.room.set_background(self.state)
                        # Reproducir sonido de interacción
                        self.interaction_sound.play()
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
                            # Reproducir sonido de interacción
                            self.interaction_sound.play()
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
                                # Reproducir sonido de interacción
                                self.interaction_sound.play()
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
