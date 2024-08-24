import pygame
import sys
import os
from pygame.locals import *
import random

MOVES_LIST = {"Left": (-5, 0), "Right": (5, 0), "Up": (0, -5), "Down": (0, 5)}

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Screen dimensions
RESOLUTION = (1050, 650)
WIDTH, HEIGHT = RESOLUTION
class Character:
    def __init__(self, filename, x, y):
        self.image = pygame.transform.scale(pygame.image.load(os.path.join(filename)), (40, 40))
        self.rect = pygame.Rect(x, y, self.image.get_width(), self.image.get_height())
        self.is_trapped = False

    def move_character(self, direction):
        temp_character = self.rect.move(direction)
        if temp_character.collidelist(walls) == -1 and not self.is_trapped:
            self.rect = temp_character

    def reset_position(self, position):
        self.rect.topleft = position


class Spider:
    def __init__(self, filename, x, y):
        self.image = pygame.transform.scale(pygame.image.load(os.path.join(filename)), (50, 50))
        self.rect = pygame.Rect(x, y, self.image.get_width(), self.image.get_height())
        # Spider moves

        self.direction = random.choice(list(MOVES_LIST.values()))
        self.steps = random.randint(150, 200)

    def move_spider(self):
        temp_spider = self.rect.move(self.direction)
        if temp_spider.collidelist(walls) == -1:
            self.rect = temp_spider
        else:
            # New random direction
            self.direction = random.choice(list(MOVES_LIST.values()))
        self.steps -= 1
        if self.steps == 0:
            # New random direction and number of steps
            self.direction = random.choice(list(MOVES_LIST.values()))
            self.steps = random.randint(100, 200)

    def reset_position(self, position):
        self.rect.topleft = position


class Spiderweb:
    def __init__(self, x, y):
        self.image = pygame.transform.scale(pygame.image.load(os.path.join("images/spider_web.png")), (50, 50))
        self.rect = pygame.Rect(x, y, self.image.get_width() // 2, self.image.get_height() // 2)
        self.timer = 300


# Initialize Pygame
pygame.init()

screen = pygame.display.set_mode(RESOLUTION)
pygame.display.set_caption("Butterflies")


character1 = Character("images/pink_butterfly.png", 50, 50)
character2 = Character("images/purple_butterfly.png", WIDTH - 90, 50)
spider = Spider("images/spider.png", 500, 550)

# Load images
goal_image = pygame.transform.scale(pygame.image.load(os.path.join("images/red_flower.png")), (50, 50))
wall_image = pygame.transform.scale(pygame.image.load(os.path.join("images/textureStone.png")), (50, 50))

# Load sounds
game_over_sound = pygame.mixer.Sound(os.path.join("sounds/negative_beeps-6008.mp3"))
win_sound = pygame.mixer.Sound(os.path.join("sounds/success.wav"))
spiderweb_sound1 = pygame.mixer.Sound(os.path.join("sounds/pop.mp3"))
spiderweb_sound2 = pygame.mixer.Sound(os.path.join("sounds/pop2.mp3"))

board = pygame.Surface(RESOLUTION)

# Goal
goal = None

# Walls
walls = []


# Load maze layout from a file
def load_maze(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file]


maze = load_maze(os.path.join("layout.txt"))

# Load fonts
font = pygame.font.Font(None, 150)

running = True
won = False
lost = False
spider_webs = []

clock = pygame.time.Clock()


def draw():
    goal = None
    board.fill(WHITE)
    # Draw maze
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == '1':
                board.blit(wall_image, (x * 50, y * 50))
                walls.append(Rect(x * 50, y * 50, 50, 50))
            elif cell == 'G':
                board.blit(goal_image, (x * 50, y * 50))
                goal = (Rect(x * 50, y * 50, 50, 50))

    # Draw characters
    board.blit(character1.image, character1.rect)
    board.blit(character2.image, character2.rect)
    # Draw spider
    board.blit(spider.image, spider.rect)
    # Draw spiderweb
    for spider_web in spider_webs[:]:
        spider_web.timer -= 1
        if spider_web.timer != 0:
            board.blit(spider_web.image, spider_web.rect)
        else:
            spider_webs.remove(spider_web)
            spiderweb_sound2.play()
    # Display text if won or lost
    if won:
        text = font.render("You Won!", True, GREEN)
        board.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
    if lost:
        text = font.render("You LOST!", True, RED)
        board.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

    screen.blit(board, (0, 0))
    pygame.display.flip()
    return goal


def check_goal():
    if character1.rect.collidepoint(goal.center) and character2.rect.collidepoint(goal.center):
        return True
    return False


def check_game_over():
    if spider.rect.collidepoint(character1.rect.center) or spider.rect.collidepoint(character2.rect.center):
        return True
    return False


def check_collision_with_spiderweb(character):
    for spider_web in spider_webs:
        if character.rect.collidepoint(spider_web.rect.center):  # Check if the center point is within the rectangle
            return True
    return False


# Game loop
while running:
    goal = draw()
    if check_collision_with_spiderweb(character1):
        character1.is_trapped = True
    else:
        character1.is_trapped = False
    if check_collision_with_spiderweb(character2):
        character2.is_trapped = True
    else:
        character2.is_trapped = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
            if event.key == pygame.K_r:
                character1.reset_position((50, 50))
                character2.reset_position((WIDTH - 90, 50))
                lost = False
                won = False
                spider.reset_position((500, 550))
                spider_webs = []

    keys = pygame.key.get_pressed()

    if not lost and not won:
        if keys[K_w]:
            character1.move_character(MOVES_LIST["Up"])
            character2.move_character(MOVES_LIST["Up"])
        if keys[K_a]:
            character1.move_character(MOVES_LIST["Left"])
            character2.move_character(MOVES_LIST["Right"])
        if keys[K_s]:
            character1.move_character(MOVES_LIST["Down"])
            character2.move_character(MOVES_LIST["Down"])
        if keys[K_d]:
            character1.move_character(MOVES_LIST["Right"])
            character2.move_character(MOVES_LIST["Left"])

        spider.move_spider()

        # Place a spiderweb
        random_num = random.randint(0, 150)
        if random_num == 100:
            spider_webs.append(Spiderweb(spider.rect.x, spider.rect.y))
            spiderweb_sound1.play()

        # Check if both characters have reached the goal
        if check_goal():
            won = True
            
            win_sound.play()

        # Check if collide with spider
        if check_game_over():
            lost = True
            game_over_sound.play()

    clock.tick(60)

pygame.quit()
sys.exit()
