import pygame


class Wall(pygame.sprite.Sprite):
    def __init__(self, start_pos, *groups):
        super().__init__(*groups)
        self.image_name = "images/wall.png"
        self.original_image = pygame.image.load(self.image_name)
        self.image = self.original_image.copy()

        self.rect = self.image.get_rect()
        self.rect.center = start_pos

        self.position = [float(self.rect.center[0]), float(self.rect.center[1])]

    def update_sprite(self):
        pass

    def update_movement_and_collision(self):
        pass
