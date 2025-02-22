import pygame
from PIL import Image

class Character:
    def __init__(self, gif_path, x, y):
        self.gif_path = gif_path
        self.x = x
        self.y = y
        self.frames = self.load_gif_frames(gif_path)
        self.frame_index = 0
        self.frame_delay = 100
        self.last_update = pygame.time.get_ticks()
        self.flipped = False

    def load_gif_frames(self, gif_path):
        gif = Image.open(gif_path)
        frames = []
        for frame in range(gif.n_frames):
            gif.seek(frame)
            frame_image = gif.convert('RGBA')
            frame_surface = pygame.image.fromstring(frame_image.tobytes(), frame_image.size, frame_image.mode)
            frames.append(frame_surface)
        return frames

    def update(self, keys, width, height, invisible_rects, immobilized):
        if immobilized:
            return

        running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        speed = 2 + running

        new_x, new_y = self.x, self.y

        if keys[pygame.K_w] and self.y - speed >= 0:
            new_y -= speed
        if keys[pygame.K_s] and self.y + self.frames[0].get_height() + speed <= height:
            new_y += speed
        if keys[pygame.K_a] and self.x - speed >= 0:
            new_x -= speed
            self.flipped = True
        if keys[pygame.K_d] and self.x + self.frames[0].get_width() + speed <= width:
            new_x += speed
            self.flipped = False

        gif_rect_x = pygame.Rect(new_x, self.y, self.frames[0].get_width(), self.frames[0].get_height())
        gif_rect_y = pygame.Rect(self.x, new_y, self.frames[0].get_width(), self.frames[0].get_height())

        collision_x = any(gif_rect_x.colliderect(rect) for rect in invisible_rects)
        collision_y = any(gif_rect_y.colliderect(rect) for rect in invisible_rects)

        if not collision_x:
            self.x = new_x
        if not collision_y:
            self.y = new_y

        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > self.frame_delay:
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.last_update = current_time

    def move(self, x, y):
        self.x = x
        self.y = y

    def draw(self, window):
        frame = self.frames[self.frame_index]
        if self.flipped:
            frame = pygame.transform.flip(frame, True, False)
        window.blit(frame, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.frames[0].get_width(), self.frames[0].get_height())
