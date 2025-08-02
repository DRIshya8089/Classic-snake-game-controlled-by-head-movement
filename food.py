import random
import pygame

class Food:
    def __init__(self, snake_body):
        self.spawn(snake_body)
        self.bonus_active = False
        self.bonus_position = None

    def spawn(self, snake_body):
        # Updated for 25x25 grid instead of 30x30
        self.position = (random.randint(0, 24), random.randint(0, 24))
        while self.position in snake_body:
            self.position = (random.randint(0, 24), random.randint(0, 24))

    def spawn_bonus(self, snake_body):
        # Updated for 25x25 grid instead of 30x30
        self.bonus_position = (random.randint(0, 24), random.randint(0, 24))
        while self.bonus_position in snake_body:
            self.bonus_position = (random.randint(0, 24), random.randint(0, 24))
        self.bonus_active = True

    def draw(self, win):
        pygame.draw.rect(win, (255, 0, 0), (self.position[0] * 20, self.position[1] * 20, 20, 20))
        if self.bonus_active and self.bonus_position:
            pygame.draw.rect(win, (255, 255, 0), (self.bonus_position[0] * 20, self.bonus_position[1] * 20, 20, 20))
