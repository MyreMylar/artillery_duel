import pygame


class PowerGauge:
    def __init__(self, start_pos, width, height):
        
        self.width = width
        self.height = height

        self.position = [start_pos[0], start_pos[1]]

        self.power_gauge_base = pygame.image.load("images/power_gauge.png").convert_alpha()

        self.base_rect = pygame.Rect(self.position[0], self.position[1], self.width, self.height)
        self.power_rect = pygame.Rect(self.position[0] + 48, self.position[1] + 4, 1, self.height - 2)

    def update_power_level(self, power_level):
        power_width = self.lerp(0.0, self.width - 2.0, power_level)
        self.power_rect = pygame.Rect(self.position[0] + 48, self.position[1] + 4, int(power_width), self.height - 2)

    def draw(self, screen):
        screen.blit(self.power_gauge_base, self.position)
        pygame.draw.rect(screen, pygame.Color("#B41E1E"), self.power_rect, 0)

    @staticmethod
    def lerp(a, b, c):
        return (c * b) + ((1.0 - c) * a)
