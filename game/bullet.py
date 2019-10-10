import math
import pygame


class Bullet(pygame.sprite.Sprite):
    def __init__(self, start_pos, initial_heading_vector, power_ups, can_split, *groups):

        super().__init__(*groups)
        self.can_split = can_split
        self.image_name = "images/bullet.png"
        self.original_image = pygame.image.load(self.image_name)
        self.image = self.original_image.copy()
        self.player_power_ups = power_ups
                
        self.rect = self.image.get_rect()
        self.rect.center = start_pos

        self.current_vector = [initial_heading_vector[0], initial_heading_vector[1]]

        self.position = [float(self.rect.center[0]), float(self.rect.center[1])]

        self.should_die = False
        self.life_time = 8.0

    def update_sprite(self, all_bullet_sprites):
        all_bullet_sprites.add(self)
        return all_bullet_sprites

    def update_movement_and_collision(self, walls, ground_rect, time_delta, wind):
        if self.position[1] > ground_rect.top:
            self.should_die = True

        for wall in walls:
            if self.test_wall_collision(wall):
                self.should_die = True

        if self.rect.colliderect(ground_rect):
            self.should_die = True
                
        # apply gravity 10 pixels per second vertically down
        gravity_force = [0.0, 200.0 * time_delta]
        self.current_vector[0] = self.current_vector[0] + gravity_force[0]
        self.current_vector[1] = self.current_vector[1] + gravity_force[1]

        # apply wind force
        wind_force = [2.0 * time_delta * wind, 0.0]
        self.current_vector[0] = self.current_vector[0] + wind_force[0]
        self.current_vector[1] = self.current_vector[1] + wind_force[1]
        
        self.position[0] += (self.current_vector[0] * time_delta)
        self.position[1] += (self.current_vector[1] * time_delta)
        self.rect.center = (int(self.position[0]), int(self.position[1]))

        # calc facing angle
        direction_magnitude = math.sqrt(self.current_vector[0] ** 2 + self.current_vector[1] ** 2)
        unit_dir_vector = [0, 0]
        if direction_magnitude > 0.0:
            unit_dir_vector = [self.current_vector[0] / direction_magnitude,
                               self.current_vector[1] / direction_magnitude]
        facing_angle = math.atan2(-unit_dir_vector[0], -unit_dir_vector[1])*180/math.pi

        bullet_centre_position = self.rect.center
        self.image = pygame.transform.rotate(self.original_image, facing_angle)
        self.rect = self.image.get_rect()
        self.rect.center = bullet_centre_position

        self.life_time -= time_delta
        if self.life_time <= 0.0:
            self.should_die = True

    def test_wall_collision(self, wall):
        collided = False
        if self.rect.colliderect(wall.rect):
            collided = True
        return collided
