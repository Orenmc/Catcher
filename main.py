from abc import abstractmethod
import pygame
import os
import json
import logging
from typing import List
import random


class ImageDrawable:
    def __init__(self, x, y, image_path, win_size):
        self.x = x
        self.y = y
        self.win_width, self.win_height = win_size

        try:
            self.img = pygame.image.load(image_path)
        except:
            logging.error('can not find {}'.format(image_path))
            raise


    @abstractmethod
    def draw(self):
        pass

    @abstractmethod
    def move(self):
        pass


class Parachute:

    def __init__(self, x, y, win_height):
        # TODO: check if img not available - maybe add try/catch
        self.x = x
        self.y = y
        self.img = pygame.image.load(os.path.join('view', 'parachute.png'))
        self.vel = 2
        self.isPassed = False
        self.win_height = win_height
        self.img_height = self.img.get_height()
        self.hit_box = pygame.Rect(self.x, self.y + self.img.get_width() - 10, self.img.get_width(), 10)

    def move(self):
        self.y += self.vel

        self.hit_box = pygame.Rect(self.x, self.y + self.img.get_width() - 10, self.img.get_width(), 10)

        if self.y > self.win_height:
            self.isPassed = True

    def draw(self, window: pygame.Surface):
        window.blit(self.img, (self.x, self.y))
        pygame.draw.rect(window, (255, 0, 0), self.hit_box, 2)


class Airplane:

    def __init__(self, win_width, para_list: List[Parachute]):
        # TODO: check if img not available - maybe add try/catch
        self.img = pygame.transform.flip(
            pygame.transform.scale2x(pygame.image.load(os.path.join('view', 'airplane.png'))), True, False)
        self.win_width = win_width
        self.img_width = self.img.get_width()
        self.x = self.win_width
        self.y = 0
        self.vel = 3
        self.para_list = para_list
        self.drop_parachute_x = random.randint(0 + self.img_width, self.win_width - self.img_width)
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
            self.x = self.win_width

    def draw(self, window: pygame.Surface):
        window.blit(self.img, (self.x, self.y))


class Player:

    def __init__(self):
        # TODO: check if img not available - maybe add try/catch
        self.img = pygame.image.load(os.path.join('view', 'boat.png'))
        self.x = 400  # TODO: change magic numbers
        self.y = 600 - self.img.get_height()
        self.vel = 3
        self.hit_box = pygame.Rect(self.x, self.y + round(self.img.get_height() * 0.67), self.img.get_width(), 20)

    def move(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and self.x > self.vel:
            self.x -= self.vel

        if keys[pygame.K_RIGHT] and self.x < 800 - self.vel - self.img.get_width():  # TODO: change magic numbers
            self.x += self.vel

        self.hit_box = pygame.Rect(self.x, self.y + round(self.img.get_height() * 0.67), self.img.get_width(), 20)

    def draw(self, window: pygame.Surface):
        window.blit(self.img, (self.x, self.y))
        pygame.draw.rect(window, (255, 0, 0), self.hit_box, 2)


class Base:
    def __init__(self):
        # TODO: check if img not available - maybe add try/catch
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


class GameLogic:

    def __init__(self, window: pygame.Surface):
        self.win = window
        self.score: int = 0
        self.lives: int = 3
        self.images = list()
        self.pause: bool = False
        self.END_GAME: bool = False
        self.para_list: List[Parachute] = list()
        self.player = Player()

    def move_all(self):
        if not self.pause:
            # moving all images except parachutes
            for img in self.images:
                img.move()
            # moving parachutes images
            for para in self.para_list:
                para.move()

    def draw_all(self):
        if self.pause:
            # adding the content of draw_pause
            # TODO change magic numbers
            font = pygame.font.SysFont('comicsans', 200)
            text = font.render('Paused', 1, (255, 0, 0))
            self.win.blit(text, (100, 200))
            pygame.display.update()
        else:
            # adding the content of draw_window
            # TODO: change magic numbers
            # background:
            self.win.fill((98, 47, 186))
            # score
            font = pygame.font.SysFont(name='david', size=30, bold=True)
            text = font.render('score: {}'.format(self.score), 1, (0, 0, 0))
            self.win.blit(text, (0, 0))
            # lives:
            text = font.render('lives: {}'.format(self.lives), 1, (0, 0, 0))
            self.win.blit(text, (800 - text.get_width(), 0))
            # images (without parachutes)
            for img in self.images:
                img.draw(self.win)
            # parachutes images
            for para in self.para_list:
                para.draw(self.win)

            pygame.display.update()

    def init(self):
        # TODO: check how to create the list of images, maybe remove all variables s.t: base, player, and more
        self.images.append(Base())
        self.images.append(Airplane(self.win.get_width(), self.para_list))
        self.images.append(self.player)

    def game_status(self):
        for para in self.para_list:
            # check for collisions
            if self.player.hit_box.colliderect(para.hit_box):
                self.score_update(10)
                self.para_list.remove(para)

            # check for lives updates
            if para.isPassed:
                self.para_list.remove(para)
                self.lives -= 1
                if self.lives <= 0:
                    self.END_GAME = True

    def score_update(self, x):
        self.score += x

    def pause_update(self):
        self.pause = not self.pause


def main() -> None:
    global wind

    run = True
    game = GameLogic(wind)
    game.init()

    # TODO: adding pregame loop display (with info and keyboards) - can added to the gameloop,
    # TODO: but I prefer to make a new loop!

    while run:
        clock.tick(win_cfg["clock"])
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                run = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game.pause_update()
        # check game logic status (update score, update life, remove finished parachutes, check collisions)

        game.move_all()

        game.draw_all()

        game.game_status()

        if game.END_GAME:
            run = False

    pygame.quit()


if __name__ == '__main__':
    # TODO: make global!! eg. win width ans height, (clock?) and more
    logging.basicConfig(filename='basic.log', level=logging.DEBUG, format='%(asctime)s: %(levelname)s: %(message)s')

    try:
        cfg = json.load(open('config.json'))

    except OSError:
        logging.error('config file is missing')
        raise

    os.environ['SDL_VIDEO_CENTERED'] = '1'

    pygame.init()
    win_cfg = cfg["win"]
    wind = pygame.display.set_mode((win_cfg["width"], win_cfg["height"]))
    pygame.display.set_caption(win_cfg["caption"])
    clock = pygame.time.Clock()

    main()
