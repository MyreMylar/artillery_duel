import math
import pygame
import random
from pygame.locals import *
from game.bullet import Bullet


# -------------------------------------------
# We use this PowerUps class in challenge 3
# -------------------------------------------
class PowerUps:
    def __init__(self):
        self.explosion_size = 12
        self.max_shots = 1
        self.clusters_per_shell = 0


class StartLocation:
    def __init__(self, x_min, x_max, y_pos):
        self.x_min = x_min
        self.x_max = x_max
        self.y_pos = y_pos
        self.position = [random.randint(self.x_min, self.x_max), self.y_pos]

    def randomise_start(self):
        self.position = [random.randint(self.x_min, self.x_max), self.y_pos]


class Scheme:
    def __init__(self):
        self.fire = K_RSHIFT
        self.detonate = K_RCTRL
        self.left = K_LEFT
        self.right = K_RIGHT


class TurretBase(pygame.sprite.Sprite):
    def __init__(self, start_location, *groups):
        super().__init__(*groups)

        self.image = pygame.image.load("images/artillery_base.png")
        self.rect = self.image.get_rect()
        self.rect.center = start_location.position


class TurretBarrel(pygame.sprite.Sprite):
    def __init__(self, start_location, *groups):
        super().__init__(*groups)
        self.original_turret_image = pygame.image.load("images/turret.png")

        self.image = self.original_turret_image.copy()
        self.rect = self.image.get_rect()
        self.turret_y_offset = -12.0
        self.rect.center = [start_location.position[0], start_location.position[1] + self.turret_y_offset]


class Player:
    def __init__(self, idf, start_location, control_scheme, power_gauge, current_lives, power_ups):

        self.current_lives = current_lives

        # -------------------------------------
        # We use this variable in challenge 3
        # -------------------------------------
        self.power_ups = power_ups

        self.player_id = idf
        self.scheme = control_scheme
        self.start_location = start_location

        self.turret_base = TurretBase(start_location)
        self.turret_barrel = TurretBarrel(start_location)

        self.owned_bullets = []
        
        self.power_level = 0.0
        self.power_gauge = power_gauge

        self.should_move_left = False
        self.should_move_right = False
        
        self.should_die = False

        self.charging_power = False
        self.should_fire_bullet = False
        self.should_detonate_or_split = False

        self.current_turret_angle = 0.0

        self.min_rotate_speed = 16.0
        self.max_rotate_speed = 300.0
        self.move_left_acceleration = 0.0
        self.move_right_acceleration = 0.0
       
        self.position = [float(start_location.position[0]), float(start_location.position[1])]

    # -------------------------------------------------------------------------------
    # CHALLENGE 3
    # -------------
    #
    # Add two randomly picked 'power up' effects to the function below to make things easier
    # for the player that is currently losing. All the power up variables are contained in the
    # player's 'self.power_ups' variable. The 'class' that contains these variables
    # is at the top of this file.
    #
    # (GUIDELINE 12 LINES)
    #
    # The three available power ups are:
    #
    # - increased explosion size (try increasing it by 8)
    # - Cluster shells that appear when a shot is detonated mid air (try adding one cluster each time)
    # - More simultaneous shots (again try adding one each time)
    #
    # Hint
    # -----
    # - You will need to test the random numbers generated below with if statements
    #   so that you have a shot at getting all 3.
    # - You could use another helper function here that takes a random number, to
    #   avoid having to write the same code twice.
    # -------------------------------------------------------------------------------
    def activate_random_power_up(self):
        # this function is called when the player dies
        power_up_choice_1 = random.randint(1, 3)
        power_up_choice_2 = random.randint(1, 3)

    def create_fired_bullets(self, bullets):
        if self.should_fire_bullet:
            self.should_fire_bullet = False
            fire_power = self.lerp(100.0, 600.0, self.power_level)
            heading = math.radians(90.0 - float(self.current_turret_angle))
            heading_vector = [-math.cos(heading), -math.sin(heading)]
            vel_heading_vector = [heading_vector[0] * fire_power, heading_vector[1] * fire_power]

            # we want to start bullets a little in front of the tank so they don't
            # immediately overlap with the tank that fires them and blow it up
            tank_front = [self.position[0], self.position[1]]
            tank_front[0] += heading_vector[0] * 32.0
            tank_front[1] += heading_vector[1] * 32.0

            bullet = Bullet(tank_front, vel_heading_vector, self.power_ups, True)
            bullets.append(bullet)
            self.owned_bullets.append(bullet)
            self.power_level = 0.0
        return bullets    
    
    def update_sprite(self, all_sprites):
        all_sprites.add(self.turret_barrel)
        all_sprites.add(self.turret_base)
        return all_sprites

    def process_event(self, event):
        if event.type == KEYDOWN:     
            if event.key == self.scheme.left:
                self.should_move_left = True
                self.should_move_right = False
            if event.key == self.scheme.right:
                self.should_move_right = True
                self.should_move_left = False
            if event.key == self.scheme.fire:
                if len(self.owned_bullets) < self.power_ups.max_shots:
                    self.charging_power = True
            if event.key == self.scheme.detonate:
                self.should_detonate_or_split = True

        elif event.type == KEYUP:
            if event.key == self.scheme.left:
                self.should_move_left = False
            if event.key == self.scheme.right:
                self.should_move_right = False
            if event.key == self.scheme.fire:
                if self.charging_power:
                    self.charging_power = False
                    self.should_fire_bullet = True

    def update_movement_and_collision(self, bullets, lives_board, time_delta, explosions):
        if self.charging_power:
            self.power_level += time_delta
            self.power_gauge.update_power_level(self.power_level)
            if self.power_level >= 1.0:
                self.power_level = 1.0

        for explosion in explosions:
            if self.test_explosion_collision(explosion):
                self.should_die = True
                
        for bullet in bullets:
            if self.test_bullet_collision(bullet):
                bullet.should_die = True
                self.should_die = True

        self.owned_bullets[:] = [bullet for bullet in self.owned_bullets if not bullet.should_die]

        if self.should_detonate_or_split:
            self.should_detonate_or_split = False
            oldest_bullet_life = 10000.0
            oldest_bullet = None
            for bullet in self.owned_bullets:
                if bullet.life_time < oldest_bullet_life:
                    oldest_bullet = bullet
            if oldest_bullet is not None:
                if oldest_bullet.can_split and self.power_ups.clusters_per_shell > 0:
                    cluster_direction = 1
                    for cluster_index in range(0, self.power_ups.clusters_per_shell + 1):
                        new_vector = oldest_bullet.current_vector
                        new_vector[0] += (cluster_index * 20 * cluster_direction)
                        bullet = Bullet(oldest_bullet.position, new_vector, self.power_ups, False)
                        bullets.append(bullet)
                        self.owned_bullets.append(bullet)
                        if cluster_direction == 1:
                            cluster_direction = -1
                        else:
                            cluster_direction = 1

                oldest_bullet.should_die = True
                       
        if self.should_move_left or self.should_move_right:
            if self.should_move_right:
                if self.current_turret_angle < -90.0:
                    self.current_turret_angle = -90.0
                else:
                    self.move_left_acceleration = 0.0
                    self.move_right_acceleration += time_delta * 0.75  # 1.5 seconds ish to max speed
                    if self.move_right_acceleration > 1.0:
                        self.move_right_acceleration = 1.0
                    self.current_turret_angle -= time_delta * self.lerp(self.min_rotate_speed,
                                                                        self.max_rotate_speed,
                                                                        self.move_right_acceleration)
               
            if self.should_move_left:
                if self.current_turret_angle > 90.0:
                    self.current_turret_angle = 90.0
                else:
                    self.move_right_acceleration = 0.0
                    self.move_left_acceleration += time_delta * 0.75  # 1.5 seconds ish to max speed
                    if self.move_left_acceleration > 1.0:
                        self.move_left_acceleration = 1.0
                    self.current_turret_angle += time_delta * self.lerp(self.min_rotate_speed,
                                                                        self.max_rotate_speed,
                                                                        self.move_left_acceleration)

            self.turret_barrel.image = pygame.transform.rotate(self.turret_barrel.original_turret_image,
                                                               self.current_turret_angle)
            self.turret_barrel.rect = self.turret_barrel.image.get_rect()
            self.turret_barrel.rect.center = self.rot_point([self.position[0],
                                                             self.position[1] + self.turret_barrel.turret_y_offset],
                                                            self.position, -self.current_turret_angle)

        else:
            self.move_left_acceleration = 0.0
            self.move_right_acceleration = 0.0

        for lives in lives_board:
            if lives.player_id == self.player_id:
                lives.lives = self.current_lives
                lives.explosion_power = self.power_ups.explosion_size
                lives.clusters = self.power_ups.clusters_per_shell
                lives.shots = self.power_ups.max_shots

    def test_bullet_collision(self, bullet):
        collided = False
        if self.get_hit_box(self.turret_base.rect).colliderect(bullet.rect):
            collided = True

        return collided

    def test_explosion_collision(self, explosion):
        collided = False
        if self.get_hit_box(self.turret_base.rect).colliderect(explosion.rect):
            # test if any of corners of box are inside circle
            if (self.test_point_in_explosion(self.turret_base.rect.topleft, explosion)) or\
                    (self.test_point_in_explosion(self.turret_base.rect.topright, explosion)) or\
                    (self.test_point_in_explosion(self.turret_base.rect.bottomleft, explosion)) or\
                    (self.test_point_in_explosion(self.turret_base.rect.bottomright, explosion)):
                collided = True
        return collided
    
    @staticmethod
    def test_point_in_explosion(point, explosion):
        return (point[0] - explosion.position[0])**2 + (point[1] - explosion.position[1])**2 < explosion.radius**2
    
    @staticmethod
    def get_hit_box(rect):
        smaller_rect = rect.copy()
        original_center = rect.center
        smaller_rect.width = 28
        smaller_rect.height = 28
        smaller_rect.center = original_center
        return smaller_rect
    
    @staticmethod
    def distance_from_line(point, line):

        x1 = line[0][0]
        y1 = line[0][1]
        x2 = line[1][0]
        y2 = line[1][1]
        x3 = point[0]
        y3 = point[1]

        px = x2-x1
        py = y2-y1

        something = px*px + py*py

        u = ((x3 - x1) * px + (y3 - y1) * py) / float(something)

        if u > 1:
            u = 1
        elif u < 0:
            u = 0

        x = x1 + u * px
        y = y1 + u * py

        dx = x - x3
        dy = y - y3

        # Note: If the actual distance does not matter,
        # if you only want to compare what this function
        # returns to other results of this function, you
        # can just return the squared distance instead
        # (i.e. remove the sqrt) to gain a little performance

        dist = math.sqrt(dx*dx + dy*dy)

        return dist

    @staticmethod
    def rot_point(point, axis, ang):
        """ Orbit. calculates the new loc for a point that rotates a given num of degrees around an axis point,
        +clockwise, -anticlockwise -> tuple x,y
        """
        ang -= 90
        x, y = point[0] - axis[0], point[1] - axis[1]
        radius = math.sqrt(x*x + y*y)  # get the distance between points

        r_ang = math.radians(ang)  # convert ang to radians.

        h = axis[0] + (radius * math.cos(r_ang))
        v = axis[1] + (radius * math.sin(r_ang))

        return [h, v]

    @staticmethod
    def lerp(a, b, c):
        return (c * b) + ((1.0-c) * a)


class RespawnPlayer:
    def __init__(self, player):
        self.player_id = player.player_id
        self.control_scheme = player.scheme
        self.start_location = player.start_location
        self.start_location.randomise_start()
        self.power_gauge = player.power_gauge
        self.current_lives = player.current_lives - 1
        self.power_ups = player.power_ups
        self.respawn_timer = 2.0
        self.time_to_spawn = False
        self.has_respawned = False

    def update(self, frame_time_ms):
        self.respawn_timer -= (frame_time_ms / 1000.0)
        if self.respawn_timer < 0.0:
            self.time_to_spawn = True


class PlayerLives:
    def __init__(self, player_id, lives, screen_position):
        self.player_id = player_id
        self.screen_position = screen_position
        self.lives = lives
        self.explosion_power = 1
        self.clusters = 1
        self.shots = 1
