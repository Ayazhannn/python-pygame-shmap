import pygame
from pygame.locals import *
import random

pygame.init()

#create a window
game_width = 800
game_height = 500
screen_size =(game_width, game_height)
game_window = pygame.display.set_mode(screen_size)
pygame.display.set_caption("")
padding_y = 50

#colors

#number of ms before next bullet fire
bullet_cooldown = 500
#timestamp of last bullet fired
last_bullet_time = pygame.time.get_ticks()
#time when the next bird will spawn
next_bird = pygame.time.get_ticks()

#function for resizing the image
def scale_image(image, new_width):
    image_scale = new_width / image.get_rect().width
    new_height = image.get_rect().height * image_scale
    scaled_size = (new_width, new_height)
    return pygame.transform.scale(image, scaled_size)

#load bg image
bg = pygame.image.load('images/bg.png').convert_alpha()
bg = scale_image(bg, game_width)
bg_scroll = 0

#load and scale the airplane
airplane_imgs = []
for i in range(2):
    airplane_img = pygame.image.load(f"images/player/fly{i}.png").convert_alpha()
    airplane_img = scale_image(airplane_img, 70)
    airplane_imgs.append(airplane_img)

#load and scale the heart images for player health
heart_images = []
heart_image_index = 0
for i in range(5):
    heart_image = pygame.image.load(f"images/hearts/heart{i}.png").convert_alpha()
    heart_image = scale_image(heart_image, 30)
    heart_images.append(heart_image)

#load the nirds image
bird_colors = ['blue','grey','red','yellow']
bird_imgs = {}
for bird_color in bird_colors:
    #add a new list to the dictionary
    bird_imgs[bird_color] = []
    for i in range(4):
        bird_img = pygame.image.load(f"images/birds/{bird_color}{i}.png").convert_alpha()
        bird_img = scale_image(bird_img, 50)
        bird_img = pygame.transform.flip(bird_img, True, False)
        bird_imgs[bird_color].append(bird_img)


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):

        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y

        self.lives = 3
        self.score = 0

        #index the image to be displayed
        self.image_index = 0

        #angle of the image
        self.image_angle = 0

    def update(self):
        self.image_index += 1
        if self.image_index >= len(airplane_imgs):
            self.image_index = 0

        #assign next image
        self.image = airplane_imgs[self.image_index]
        self.rect = self.image.get_rect()

        #update the angle of image
        self.image = pygame.transform.rotate(self.image, self.image_angle)

        self.rect.x = self.x
        self.rect.y = self.y

        #check if player collides with the bird
        if pygame.sprite.spritecollide(self, bird_group, True):
            self.lives -= 1



class Bullet(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.radius = 5

        self.rect = Rect(x,y,10,10)

    def draw(self):
        pygame.draw.circle(game_window,(255, 255, 0),(self.x, self.y),self.radius)

    def update(self):
        # move bullet to the right
        self.x += 2
        self.rect.x = self.x
        self.rect.y = self.y

        #remove bullet from sprite group when it goes off screen
        if self.x > game_width:
            self.kill()

class Bird(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.x = game_width
        self.y = random.randint(padding_y, game_height - padding_y * 2)

        self.color = random.choice(bird_colors)
        self.image_index = 0

        self.image = bird_imgs[self.color][self.image_index]
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def update(self):
        self.x -=2
        self.image_index +=0.25

        if self.image_index >= len(bird_imgs[self.color]):
            self.image_index = 0

        #assign next image
        self.image = bird_imgs[self.color][int(self.image_index)]
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        #check if bird collides with bullet
        if pygame.sprite.spritecollide(self, bullet_group, True):
            self.kill()
            player.score += 1

        #remove bird from sprite group when it goes from screen
        if self.x < 0:
            self.kill()



#create the sprite groups
player_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
bird_group = pygame.sprite.Group()

#create the player
player_x = 30
player_y = game_height // 2
player = Player(player_x, player_y)
player_group.add(player)

#game loop
clock = pygame.time.Clock()
fps = 120
running = True

while running:

    clock.tick(fps)
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
    keys = pygame.key.get_pressed()

    #move airplane using up/down arow keys
    if keys[K_UP] and player.rect.top > padding_y:
        player.y -= 2
        player.image_angle = 15
    elif keys[K_DOWN] and player.rect.bottom < game_height - padding_y:
        player.y += 2
        player.image_angle = -15
    else:
        player.image_angle = 0


    #shoot bullet space bar
    if keys[K_SPACE] and last_bullet_time + bullet_cooldown < pygame.time.get_ticks():
        bullet_x = player.x + player.image.get_width()
        bullet_y = player.y + player.image.get_height() // 2
        bullet = Bullet(bullet_x, bullet_y)
        bullet_group.add(bullet)
        last_bullet_time = pygame.time.get_ticks()

    #spawn a new bird
    if next_bird < pygame.time.get_ticks():
        bird = Bird()
        bird_group.add(bird)

        #randomly pick from 0 to 3 secod to spawn a bird
        next_bird = random.randint(pygame.time.get_ticks(), pygame.time.get_ticks() + 3000)

    #draw the bg
    game_window.blit(bg, (0 - bg_scroll, 0))
    game_window.blit(bg, (game_width - bg_scroll, 0))
    bg_scroll += 1
    if bg_scroll == game_width:
        bg_scroll = 0

    #draw the player
    player_group.update()
    player_group.draw(game_window)

    #draw the bullet
    bullet_group.update()
    for bullet in bullet_group:
        bullet.draw()

    #draw the bird
    bird_group.update()
    bird_group.draw(game_window)

    #display remaining lives
    for i in range(player.lives):
        heart_image = heart_images[int(heart_image_index)]
        heart_x = 10 + i * (heart_image.get_width() + 10)
        heart_y = 10
        game_window.blit(heart_image, (heart_x, heart_y))
    heart_image_index += 0.1
    if heart_image_index >= len(heart_images):
        heart_image_index = 0

    #display the score
    font = pygame.font.Font(pygame.font.get_default_font(), 16)
    text = font.render(f"Score: {player.score}", True, (0,0,0))
    text_rect = text.get_rect()
    text_rect.center = (200,20)
    game_window.blit(text, text_rect)

    pygame.display.update()

    #check if the game is over
    while player.lives == 0:
        clock.tick(fps)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
        gameover_str = f"Game Over. Play again(y or n)?"
        font = pygame.font.Font(pygame.font.get_default_font(), 24)
        text = font.render(gameover_str, True, (255,0,0))
        text_rect = text.get_rect()
        text_rect.center = (game_width / 2, game_height / 2)
        game_window.blit(text, text_rect)

        keys = pygame.key.get_pressed()
        if keys[K_y]:
            player_group.empty()
            bird_group.empty()
            bullet_group.empty()

            #reset the player
            player = Player(player_x, player_y)
            player_group.add(player)
        elif keys[K_n]:
            running = False
            break
        pygame.display.update()

pygame.quit()