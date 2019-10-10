import os
import pygame
from pygame.locals import *

from game.player import Player, PlayerLives, Scheme, StartLocation, RespawnPlayer, PowerUps
from game.wall import Wall
from game.fire_power_gauge import PowerGauge
from game.explosion import Explosion
from game.wind import Wind
from game.wind_gauge import WindGauge


def main():

    pygame.init()
    os.environ['SDL_VIDEO_CENTERED'] = '1'  # center the window in the middle of the screen
    pygame.key.set_repeat()
    x_screen_size = 1024
    y_screen_size = 600
    pygame.display.set_caption('Artillery duel')
    screen = pygame.display.set_mode((x_screen_size, y_screen_size))

    background = pygame.image.load("images/background.png").convert()
    stats_base_image = pygame.image.load("images/stats_back.png").convert_alpha()
    all_sprites = pygame.sprite.OrderedUpdates()
    all_explosion_sprites = pygame.sprite.Group()
    all_bullet_sprites = pygame.sprite.Group()
    wall_sprites = pygame.sprite.Group()
    font = pygame.font.Font(None, 16)
    large_font = pygame.font.Font(None, 64)
    explosions_sprite_sheet = pygame.image.load("images/explosions.png").convert_alpha()

    wind = Wind(-20, 20)
    wind_gauge = WindGauge([x_screen_size/2,
                            y_screen_size - y_screen_size * 0.10], wind.min, wind.max)

    bullets = []
    lives_board = []
    walls = []
    explosions = []

    ground_rect = pygame.Rect(-2000, (y_screen_size - (y_screen_size * 0.20) + 10), 3024, (y_screen_size * 0.20) + 10)

    # move up by floor height and half wall height
    walls.append(Wall([x_screen_size/2, y_screen_size - 118 - y_screen_size * 0.20]))

    for wall in walls:
        wall_sprites.add(wall)

    player_lives = 10

    players_to_respawn = []
    players = []

    start_location1 = StartLocation(int(x_screen_size * 0.05),
                                    int(x_screen_size * 0.40),
                                    (y_screen_size - y_screen_size * 0.20))
    start_location2 = StartLocation(int(x_screen_size - x_screen_size * 0.40),
                                    int(x_screen_size - x_screen_size * 0.05),
                                    (y_screen_size - y_screen_size * 0.20))
    
    player_1_id = "Player 1"
    player_1_lives = PlayerLives(player_1_id, player_lives,
                                 (int(x_screen_size / 2) - 100,
                                  (y_screen_size - y_screen_size * 0.13)))
    lives_board.append(player_1_lives)
    
    player_2_id = "Player 2"
    player_2_lives = PlayerLives(player_2_id, player_lives,
                                 (int(x_screen_size / 2) + 100,
                                  (y_screen_size - y_screen_size * 0.13)))
    lives_board.append(player_2_lives)

    power_gauge_1_pos = [int(x_screen_size * 0.02),
                         int(y_screen_size - y_screen_size * 0.13)]
    power_gauge_2_pos = [int(x_screen_size - x_screen_size * 0.02) - 300,
                         int(y_screen_size - y_screen_size * 0.13)]
    power_gauge_1 = PowerGauge(power_gauge_1_pos, 250, 18)
    power_gauge_2 = PowerGauge(power_gauge_2_pos, 250, 18)

    player_control_scheme_1 = Scheme()
    player_control_scheme_1.fire = K_LSHIFT
    player_control_scheme_1.detonate = K_LCTRL
    player_control_scheme_1.left = K_a
    player_control_scheme_1.right = K_d

    player_control_scheme_2 = Scheme()
    
    players.append(Player(player_1_id, start_location1, player_control_scheme_1,
                          power_gauge_1, player_lives, PowerUps()))

    players.append(Player(player_2_id, start_location2, player_control_scheme_2,
                          power_gauge_2, player_lives, PowerUps()))

    clock = pygame.time.Clock()
    running = True
    is_game_over = False
    restart_game = False
    win_message = ""
    while running:
        frame_time = clock.tick(60)
        time_delta = frame_time/1000.0

        all_sprites.empty()
        all_bullet_sprites.empty()
        all_explosion_sprites.empty()
        
        # handle UI and inout events
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            for player in players:
                player.process_event(event)
            if is_game_over:
                if event.type == KEYDOWN:     
                    if event.key == K_y:
                        restart_game = True

        if restart_game:
            restart_game = False
            spawn_players(players, bullets, explosions, player_1_id, start_location1, player_control_scheme_1,
                          power_gauge_1, player_2_id, start_location2, player_control_scheme_2, power_gauge_2,
                          player_lives)
            is_game_over = False
        if is_game_over:
            for explosion in explosions:
                all_explosion_sprites = explosion.update_sprite(all_explosion_sprites, time_delta)
            explosions[:] = [explosion for explosion in explosions if not explosion.should_die]
            all_explosion_sprites.update()
        else:
            # handle re-spawning players after dying
            for respawning_player in players_to_respawn:
                if respawning_player.time_to_spawn:
                    new_player = Player(respawning_player.player_id, respawning_player.start_location,
                                        respawning_player.control_scheme, respawning_player.power_gauge,
                                        respawning_player.current_lives, respawning_player.power_ups)
                    new_player.activate_random_power_up()
                    players.append(new_player)
                    respawning_player.has_respawned = True
                else:
                    respawning_player.update(frame_time)
            players_to_respawn[:] = [r for r in players_to_respawn if not r.has_respawned]

            # update wind
            wind.update(time_delta)
            wind_gauge.update_wind_direction_and_strength(wind.current_value)
             
            # update players and bullets
            for player in players:
                bullets = player.create_fired_bullets(bullets)
                player.update_movement_and_collision(bullets, lives_board, time_delta, explosions)
                all_sprites = player.update_sprite(all_sprites)
                if player.should_die:
                    if player.current_lives > 1:
                        players_to_respawn.append(RespawnPlayer(player))
                    else:
                        for lives in lives_board:
                            if lives.player_id == player.player_id:
                                lives.lives = 0
                        is_game_over = True
                        if player.player_id == "Player 1":
                            win_message = "Player 2 wins!"
                        else:
                            win_message = "Player 1 wins!"

            players[:] = [player for player in players if not player.should_die]

            for bullet in bullets:
                bullet.update_movement_and_collision(walls, ground_rect, time_delta, wind.current_value)
                all_bullet_sprites = bullet.update_sprite(all_bullet_sprites)
                if bullet.should_die:
                    explosions.append(Explosion(bullet.position, explosions_sprite_sheet, bullet.player_power_ups))
            bullets[:] = [bullet for bullet in bullets if not bullet.should_die]

            for explosion in explosions:
                all_explosion_sprites = explosion.update_sprite(all_explosion_sprites, time_delta)
            explosions[:] = [explosion for explosion in explosions if not explosion.should_die]

            all_sprites.update()
            all_bullet_sprites.update()
            all_explosion_sprites.update()
        
        screen.blit(background, (0, 0))  # draw the background

        wall_sprites.draw(screen)
        all_sprites.draw(screen)  # draw all our moving sprites
        all_bullet_sprites.draw(screen)  # draw all our moving sprites
        all_explosion_sprites.draw(screen)  # draw all our moving sprites

        power_gauge_1.draw(screen)
        power_gauge_2.draw(screen)
        wind_gauge.draw(screen, font)

        if is_game_over:
            win_message_text_render = large_font.render(win_message,
                                                        True, pygame.Color("#FFFFFF"))
            win_message_text_render_rect = win_message_text_render.get_rect(centerx=x_screen_size/2,
                                                                            centery=(y_screen_size/2)-128)
            play_again_text_render = font.render("Play Again? Press 'Y' to restart",
                                                 True, pygame.Color("#FFFFFF"))
            play_again_text_render_rect = play_again_text_render.get_rect(centerx=x_screen_size/2,
                                                                          centery=(y_screen_size/2)-90)
            screen.blit(win_message_text_render, win_message_text_render_rect)
            screen.blit(play_again_text_render, play_again_text_render_rect)

        for lives in lives_board:
            screen.blit(stats_base_image, [lives.screen_position[0]-50, lives.screen_position[1]-18])
            score_string = "Lives: " + "{:,}".format(lives.lives)
            score_text_render = font.render(score_string, True, pygame.Color("#FFFFFF"))
            score_text_render_rect = score_text_render.get_rect(centerx=lives.screen_position[0],
                                                                centery=lives.screen_position[1])
            screen.blit(score_text_render, score_text_render_rect)
            
            shots_value_str = "Shots: " + str(lives.shots)
            shots_text_render = font.render(shots_value_str, True, pygame.Color("#FFFFFF"))
            shots_text_render_rect = shots_text_render.get_rect(centerx=lives.screen_position[0],
                                                                centery=lives.screen_position[1]+18)
            screen.blit(shots_text_render, shots_text_render_rect)

            clusters_value_str = "Clusters: " + str(lives.clusters)
            clusters_text_render = font.render(clusters_value_str, True, pygame.Color("#FFFFFF"))
            clusters_text_render_rect = clusters_text_render.get_rect(centerx=lives.screen_position[0],
                                                                      centery=lives.screen_position[1]+36)
            screen.blit(clusters_text_render, clusters_text_render_rect)

            clusters_value_str = "Blast size: " + str(lives.explosion_power)
            clusters_text_render = font.render(clusters_value_str, True, pygame.Color("#FFFFFF"))
            clusters_text_render_rect = clusters_text_render.get_rect(centerx=lives.screen_position[0],
                                                                      centery=lives.screen_position[1]+54)
            screen.blit(clusters_text_render, clusters_text_render_rect)
            
        pygame.display.flip()  # flip all our drawn stuff onto the screen

    pygame.quit()  # exited game loop so quit pygame


def spawn_players(players, bullets, explosions,
                  player_1_id, start_location_1, player_control_scheme_1, power_gauge_1,
                  player_2_id, start_location_2, player_control_scheme_2, power_gauge_2, player_lives):
    players[:] = []
    bullets[:] = []
    explosions[:] = []
    players.append(Player(player_1_id, start_location_1, player_control_scheme_1, power_gauge_1,
                          player_lives, PowerUps()))
    players.append(Player(player_2_id, start_location_2, player_control_scheme_2, power_gauge_2,
                          player_lives, PowerUps()))


if __name__ == '__main__':
    main()
