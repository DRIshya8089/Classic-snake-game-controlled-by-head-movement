import pygame

class Snake:
    def __init__(self):
        self.body = [(10, 10)]
        self.direction = 'RIGHT'
        self.new_block = False

    def move(self):
        x, y = self.body[0]
        if self.direction == 'UP':
            y -= 1
        elif self.direction == 'DOWN':
            y += 1
        elif self.direction == 'LEFT':
            x -= 1
        elif self.direction == 'RIGHT':
            x += 1
        elif self.direction == 'CENTER':
            # Don't move - snake is paused
            return

        new_head = (x, y)
        self.body.insert(0, new_head)

        if not self.new_block:
            self.body.pop()
        else:
            self.new_block = False

    def grow(self):
        self.new_block = True

    def draw(self, win):
        for segment in self.body:
            pygame.draw.rect(win, (0, 255, 0), (segment[0] * 20, segment[1] * 20, 20, 20))

    def change_direction(self, direction):
        """Prevent opposite direction movement to avoid instant death"""
        # Define opposite directions
        opposites = {
            'UP': 'DOWN',
            'DOWN': 'UP',
            'LEFT': 'RIGHT',
            'RIGHT': 'LEFT'
        }

        # Check if the new direction is opposite to current direction
        if direction in opposites and opposites[direction] == self.direction:
            # Don't allow opposite direction movement
            print(f"Cannot move in opposite direction: {self.direction} -> {direction}")
            return False
        else:
            # Allow the direction change
            self.direction = direction
            return True

    def check_collision(self):
        """Check for both boundary and self collision (legacy method)"""
        head = self.body[0]
        return (head in self.body[1:] or
                head[0] < 0 or head[0] >= 30 or
                head[1] < 0 or head[1] >= 30)

    def check_self_collision(self):
        """Check only for self collision (head hits body)"""
        head = self.body[0]
        return head in self.body[1:]
