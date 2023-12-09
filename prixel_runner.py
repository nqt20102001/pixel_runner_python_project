import pygame
from sys import exit
from random import randint, choice

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.player_walk_1 = pygame.image.load('graphics/player/player_walk_1.png').convert_alpha()
        self.player_walk_2 = pygame.image.load('graphics/player/player_walk_2.png').convert_alpha()
        self.player_jump = pygame.image.load('graphics/player/jump.png').convert_alpha()
        self.player_sit = pygame.image.load('graphics/player/player_sit.png').convert_alpha()

        self.player_walk = [self.player_walk_1, self.player_walk_2]
        self.player_index = 0
        self.image = self.player_walk[self.player_index]
        self.rect = self.image.get_rect(midbottom=(80, 300))
        self.original_height = self.rect.height
        self.gravity = 0
        self.is_jumping = False
        self.is_sitting = False

        self.jump_sound = pygame.mixer.Sound('audio/jump.mp3')
        self.jump_sound.set_volume(0.5)

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.rect.bottom >= 300 and not self.is_jumping:
            self.jump()

        if keys[pygame.K_DOWN] and not self.is_sitting:
            self.sit()
        elif not keys[pygame.K_DOWN] and self.is_sitting:
            self.stand_up()

    def jump(self):
        self.gravity = -20
        self.is_jumping = True
        self.jump_sound.play()

    def sit(self):
        self.is_sitting = True
        self.player_index = 0
        self.image = pygame.transform.scale(self.player_sit, (self.rect.width, 40))
        self.rect = self.image.get_rect(midbottom=self.rect.midbottom)

    def stand_up(self):
        self.is_sitting = False
        self.image = self.player_walk[int(self.player_index)]
        self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
        self.rect.height = self.original_height

    def apply_gravity(self):
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom >= 300:
            self.rect.bottom = 300
            self.is_jumping = False

    def animate_walk(self):
        self.player_index += 0.1
        if self.player_index >= len(self.player_walk):
            self.player_index = 0
        self.image = self.player_walk[int(self.player_index)]

    def animation_state(self):
        if self.is_sitting:
            pass
        elif self.rect.bottom < 300:
            self.image = self.player_jump
        else:
            self.animate_walk()

    def update(self):
        self.player_input()
        self.apply_gravity()
        self.animation_state()

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, type, speed):
        super().__init__()

        if type == 'fly':
            frames = [pygame.image.load(f'graphics/fly/fly{i}.png').convert_alpha() for i in range(1, 3)]
            y_pos_options = [210, 260]
        else:
            frames = [pygame.image.load(f'graphics/snail/snail{i}.png').convert_alpha() for i in range(1, 3)]
            y_pos_options = [300]

        self.frames = frames
        self.animation_index = 0
        self.image = self.frames[int(self.animation_index)]
        y_pos = choice(y_pos_options)
        self.rect = self.image.get_rect(midbottom=(randint(900, 1100), y_pos))
        self.speed = speed

    def animation_state(self):
        self.animation_index += 0.1
        if self.animation_index >= len(self.frames):
            self.animation_index = 0
        self.image = self.frames[int(self.animation_index)]

    def update(self):
        self.animation_state()
        self.rect.x -= self.speed
        self.destroy()

    def destroy(self):
        if self.rect.x <= -100:
            self.kill()

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 400))
        pygame.display.set_caption('Runner')
        self.clock = pygame.time.Clock()
        self.test_font = pygame.font.Font('font/Pixeltype.ttf', 50)
        self.game_active = False
        self.start_time = 0
        self.score = 0
        self.bg_music = pygame.mixer.Sound('audio/music.wav')
        self.bg_music.play(loops=-1)
        self.player = pygame.sprite.GroupSingle()
        self.player.add(Player())
        self.obstacle_group = pygame.sprite.Group()
        self.sky_surface = pygame.image.load('graphics/Sky.png').convert()
        self.ground_surface = pygame.image.load('graphics/ground.png').convert()
        self.player_stand = pygame.image.load('graphics/player/player_stand.png').convert_alpha()
        self.player_stand = pygame.transform.rotozoom(self.player_stand, 0, 2)
        self.player_stand_rect = self.player_stand.get_rect(center=(400, 200))
        self.game_name = self.test_font.render('Pixel Runner', False, (111, 196, 169))
        self.game_name_rect = self.game_name.get_rect(center=(400, 80))
        self.game_message = self.test_font.render('Press space to run', False, (111, 196, 169))
        self.game_message_rect = self.game_message.get_rect(center=(400, 330))
        self.initial_obstacle_speed = 6
        self.obstacle_timer = pygame.USEREVENT + 1
        pygame.time.set_timer(self.obstacle_timer, 1500)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:   
                    pygame.quit()
                    exit()

                if self.game_active:
                    if event.type == self.obstacle_timer:
                        current_time = int(pygame.time.get_ticks() / 1000) - self.start_time
                        obstacle_speed = self.initial_obstacle_speed + current_time // 10
                        self.obstacle_group.add(
                            Obstacle(choice(['fly', 'snail', 'snail', 'fly', 'snail', 'fly']), obstacle_speed))

                else:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        self.game_active = True
                        self.start_time = int(pygame.time.get_ticks() / 1000)

            if self.game_active:
                self.screen.blit(self.sky_surface, (0, 0))
                self.screen.blit(self.ground_surface, (0, 300))
                self.score = self.display_score()

                self.player.draw(self.screen)
                self.player.update()

                self.obstacle_group.draw(self.screen)
                self.obstacle_group.update()

                self.game_active = self.collision_sprite()

            else:
                self.screen.fill((94, 129, 162))
                self.screen.blit(self.player_stand, self.player_stand_rect)

                score_message = self.test_font.render(f'Your score: {self.score}', False, (111, 196, 169))
                score_message_rect = score_message.get_rect(center=(400, 330))
                self.screen.blit(self.game_name, self.game_name_rect)

                if self.score == 0:
                    self.screen.blit(self.game_message, self.game_message_rect)
                else:
                    self.screen.blit(score_message, score_message_rect)

            pygame.display.update()
            self.clock.tick(60) 

    def display_score(self):
        current_time = int(pygame.time.get_ticks() / 1000) - self.start_time
        score_surf = self.test_font.render(f'Score: {current_time}', False, (64, 64, 64))
        score_rect = score_surf.get_rect(center=(400, 50))
        self.screen.blit(score_surf, score_rect)
        return current_time

    def collision_sprite(self):
        if pygame.sprite.spritecollide(self.player.sprite, self.obstacle_group, False):
            self.obstacle_group.empty()
            return False
        else:
            return True


if __name__ == "__main__":
    game = Game()
    game.run()