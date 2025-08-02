import pygame

class Game:
    def __init__(self):
        self.score = 0

    def increase_score(self, amount=1):
        self.score += amount

    def draw_grid(self, win):
        for x in range(0, 600, 20):
            pygame.draw.line(win, (40, 40, 40), (x, 0), (x, 600))
        for y in range(0, 600, 20):
            pygame.draw.line(win, (40, 40, 40), (0, y), (600, y))

    def draw_score(self, win):
        font = pygame.font.SysFont('Arial', 30)
        text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        win.blit(text, (10, 10))
