import pygame
import json
import os
from itertools import cycle

class Room:
    def __init__(self, name, backgrounds, invisible_rects, blue_squares, green_squares, yellow_squares, red_squares):
        self.name = name
        self.backgrounds = backgrounds
        self.invisible_rects = invisible_rects
        self.blue_squares = [
            {"rect": pygame.Rect(*square[:4]), "target_room": square[4], "spawn_coords": (square[5], square[6]), "states": square[7], "next_state": square[8] if len(square) > 8 else None}
            for square in blue_squares
        ]
        self.green_squares = [
            {"rect": pygame.Rect(*square[:4]), "text": square[4], "states": square[5], "next_state": square[6] if len(square) > 6 else None}
            for square in green_squares
        ]
        self.yellow_squares = [
            {"rect": pygame.Rect(*square[:4]), "image": pygame.image.load(square[4]), "states": square[5], "next_state": square[6] if len(square) > 6 else None}
            for square in yellow_squares
        ]
        self.red_squares = [
            {
                "rect": pygame.Rect(*square[:4]),
                "code": square[4],
                "image_path": square[5],
                "image": pygame.image.load(square[5]) if os.path.exists(square[5]) else None,
                "code_prompt": square[6] if len(square) > 6 else "Enter code:",
                "states": square[7],
                "next_state": square[8] if len(square) > 8 else None,
                "text_bubble": pygame.image.load("data\\textures\\textboxes\\Bombolla_text.png")
            }
            for square in red_squares
        ]
        
        self.current_background = None
        self.animated_backgrounds = []
        self.background_cycle = None
        self.animation_index = 0

    def set_background(self, state):
        for background in self.backgrounds:
            if state not in background[1]:
                if isinstance(background[0], list):
                    self.animated_backgrounds = [pygame.image.load(frame) for frame in background[0]]
                    self.background_cycle = cycle(self.animated_backgrounds)
                    self.current_background = next(self.background_cycle)
                else:
                    self.current_background = pygame.image.load(background[0])
                break

    def update_animation(self):
        if self.animated_backgrounds:
            self.current_background = next(self.background_cycle)

    @staticmethod
    def load_from_json(json_path, room_name):
        with open(json_path, 'r') as file:
            data = json.load(file)
        room_data = data[room_name]
        invisible_rects = [pygame.Rect(*rect) for rect in room_data['invisible_rects']]
        room = Room(room_name, room_data['background'], invisible_rects, room_data['blue_squares'], room_data['green_squares'], room_data.get('yellow_squares', []), room_data.get('red_squares', []))
        return room

    def draw(self, window):
        if self.current_background:
            window.blit(self.current_background, (0, 0))
        for rect in self.invisible_rects:
            pygame.draw.rect(window, (255, 0, 0), rect, 1)
        for square in self.blue_squares:
            pygame.draw.rect(window, (0, 0, 255), square["rect"])
        for square in self.green_squares:
            pygame.draw.rect(window, (0, 255, 0), square["rect"])
        for square in self.yellow_squares:
            pygame.draw.rect(window, (255, 255, 0), square["rect"])
        for square in self.red_squares:
            pygame.draw.rect(window, (255, 0, 0), square["rect"])