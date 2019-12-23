import pygame
import os
import json
import logging
from typing import List
import random


class Parachute:

    def __init__(self, x, y, win_height):
        self.x = x
        self.y = y
        self.img = pygame.image.load(os.path.join('view', 'parachute.png'))
        self.vel = 2
        self.isPassed = False
        self.win_height = win_height
        self.img_height = self.img.get_height()

    def move(self):
        self.y += self.vel

        if self.y > self.win_height:
            self.isPassed = True

    def draw(self, window: pygame.Surface):
        window.blit(self.img, (self.x, self.y))


class Airplane:

    def __init__(self, win_width, para_list: List[Parachute]):
        self.img = pygame.transform.flip(
            pygame.transform.scale2x(pygame.image.load(os.path.join('view', 'airplane.png'))), True, False)
        self.win_width = win_width
        self.img_width = self.img.get_width()
        self.x = self.win_width
        self.y = 0
        self.vel = 3
        self.para_list = para_list
        self.drop_parachute_x = random.randint(0 + self.img_width, self.win_width - self.img_width)
        print('is this it? {}'.format(self.drop_parachute_x))
        self.isDrop = False

    def move(self):
        self.x -= self.vel
        if self.x < self.drop_parachute_x and not self.isDrop:
            # TODO: change win height to global and win width!
            self.para_list.append(Parachute(self.x, 0, win_height=600))
            self.isDrop = True
        if self.x < -self.img_width:
            self.isDrop = False
            self.drop_parachute_x = random.randint(0 + self.img_width, self.win_width - self.img_width)
            print('x value is: {}'.format(self.drop_parachute_x))
            self.x = self.win_width

    def draw(self, window: pygame.Surface):
        window.blit(self.img, (self.x, self.y))


class Boat:

    def __init__(self):
        self.img = pygame.image.load(os.path.join('view', 'boat.png'))
        self.x = 400  # TODO
        self.y = 600 - self.img.get_height()
        self.vel = 3

    def move(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and self.x > self.vel:
            self.x -= self.vel

        if keys[pygame.K_RIGHT] and self.x < 800 - self.vel - self.img.get_width():  # TODO:
            self.x += self.vel

    def draw(self, window: pygame.Surface):

        window.blit(self.img, (self.x, self.y))


class Base:
    def __init__(self):
        self.img1 = pygame.image.load(os.path.join('view', 'waves.png'))
        self.img2 = pygame.transform.flip(self.img1, True, False)
        self.width = self.img1.get_width()
        self.y = 0
        self.x1 = 0
        self.x2 = -self.width
        self.vel = 1

    def move(self):
        self.x1 += self.vel
        self.x2 += self.vel
        if self.x1 > self.width:
            self.x1 = self.x2 - self.width

        if self.x2 > self.width:
            self.x2 = self.x1 - self.width

    def draw(self, window):
        window.blit(self.img1, (self.x1, self.y))
        window.blit(self.img2, (self.x2, self.y))


def draw_window(window: pygame.Surface, base: Base, airplane: Airplane, parachutes: List[Parachute], boat: Boat,
                score: int):
    window.fill((98, 47, 186))
    font = pygame.font.SysFont(name='david', size=30, bold=True)
    text = font.render('score: {}'.format(score), 1, (0, 0, 0))
    window.blit(text, (0, 0))
    base.draw(window)
    airplane.draw(window)
    boat.draw(window)

    for para in parachutes:
        para.draw(window)

    pygame.display.update()


def pause_draw():
    # TODO
    font = pygame.font.SysFont('comicsans', 115)
    text = font.render('Paused', 1, (0, 0, 0))
    win.blit(text, (0, 250))
    pygame.display.update()


def main() -> None:
    base = Base()
    # para_list = [Parachute(250, 0, win.get_height()), Parachute(400, 200, win.get_height())]
    para_list = []
    airplane = Airplane(win.get_width(), para_list)
    boat = Boat()  # TODO
    score = 0
    run = True
    pause = False

    while run:
        clock.tick(win_cfg["clock"])
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                pause = not pause
                print(pause)

        if pause:
            pause_draw()

        else:
            boat.move()
            base.move()
            airplane.move()

            for para in para_list:
                para.move()

                if para.isPassed:
                    para_list.remove(para)
                    score += 10

            draw_window(win, base, airplane, para_list, boat, score)

    pygame.quit()


if __name__ == '__main__':
    logging.basicConfig(filename='basic.log', level=logging.DEBUG, format='%(asctime)s: %(levelname)s: %(message)s')

    try:
        cfg = json.load(open('config.json'))

    except OSError:
        logging.error('config file is missing')
        raise

    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.init()
    win_cfg = cfg["win"]
    win = pygame.display.set_mode((win_cfg["width"], win_cfg["height"]))
    pygame.display.set_caption(win_cfg["caption"])
    clock = pygame.time.Clock()

    main()
