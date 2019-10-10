import pygame


class WindGauge:
    def __init__(self, start_pos, wind_min, wind_max):

        self.wind_min = wind_min
        self.wind_max = wind_max
        
        self.radius = 24
        self.position = [int(start_pos[0]), int(start_pos[1])]
        self.wind_direction_point = [int(self.position[0]), int(self.position[1]) - self.radius + 2]
        self.wind_direction_arrow_corner_1 = [int(self.position[0] + 4), int(self.position[1]) - self.radius + 6]
        self.wind_direction_arrow_corner_2 = [int(self.position[0] - 4), int(self.position[1]) - self.radius + 6]

        self.wind_strength_text = "0"

        self.center_position = [self.position[0] - 40, self.position[1] - 40]
        self.wind_gauge_base = pygame.image.load("images/wind_gauge.png").convert_alpha()

    def update_wind_direction_and_strength(self, strength):
        if strength == 0:
            self.wind_strength_text = "0"
            self.wind_direction_point = [int(self.position[0]), int(self.position[1]) - self.radius + 2]
            self.wind_direction_arrow_corner_1 = [int(self.position[0] + 4), int(self.position[1]) - self.radius + 6]
            self.wind_direction_arrow_corner_2 = [int(self.position[0] - 4), int(self.position[1]) - self.radius + 6]
        elif strength < 0:
            self.wind_strength_text = str(abs(strength))
            point_position = 10 + ((self.radius - 10) * (abs(strength) / abs(self.wind_min)))
            self.wind_direction_point = [int(self.position[0] - point_position), int(self.position[1])]
            self.wind_direction_arrow_corner_1 = [int(self.position[0] - point_position + 4), int(self.position[1]) + 4]
            self.wind_direction_arrow_corner_2 = [int(self.position[0] - point_position + 4), int(self.position[1]) - 4]
        elif strength > 0:
            self.wind_strength_text = str(strength)
            point_position = 10 + ((self.radius - 10) * (abs(strength) / abs(self.wind_max)))
            self.wind_direction_point = [int(self.position[0] + point_position), int(self.position[1])]
            self.wind_direction_arrow_corner_1 = [int(self.position[0] + point_position - 4), int(self.position[1]) + 4]
            self.wind_direction_arrow_corner_2 = [int(self.position[0] + point_position - 4), int(self.position[1]) - 4]

    def draw(self, screen, font):
        screen.blit(self.wind_gauge_base, self.center_position)
        pygame.draw.line(screen, pygame.Color("#000000"), self.position, self.wind_direction_point, 2)
        pygame.draw.line(screen, pygame.Color("#000000"), self.wind_direction_point,
                         self.wind_direction_arrow_corner_1, 2)
        pygame.draw.line(screen, pygame.Color("#000000"), self.wind_direction_point,
                         self.wind_direction_arrow_corner_2, 2)
        
        strength_text_render = font.render(self.wind_strength_text, True, pygame.Color("#000000"))
        strength_text_render_rect = strength_text_render.get_rect(centerx=self.position[0], centery=self.position[1]+32)
        screen.blit(strength_text_render, strength_text_render_rect)

    @staticmethod
    def lerp(a, b, c):
        return (c * b) + ((1.0 - c) * a)
