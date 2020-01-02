from abc import abstractmethod
import pygame
import os
import json
import logging
from typing import List
import random


class ImageDrawable:
    """
    an abstract class, for all Drawable surfaces/images that Can been drawn on the window surface
    """

    def __init__(self, x: int, y: int, image_path: str, vel: int, win_size: (int, int)):
        """
        :param x: x position
        :param y: y position
        :param image_path: path to image
        :param vel: velocity of image
        :param win_size: size of the window surface (width, height)
        """
        try:
            self.img = pygame.image.load(image_path)
        except pygame.error as e:
            logging.error(e)
            raise
        self.x = x
        self.y = y
        self.win_width, self.win_height = win_size
        self.vel = vel

    @abstractmethod
    def draw(self, window: pygame.Surface) -> None:
        """
        drawing on window surface
        :param window: window surface (which will be drawn on)
        :return: None
        """
        pass

    @abstractmethod
    def move(self) -> None:
        """
        move the image according to its velocity
        :return: None
        """
        pass


class Parachute(ImageDrawable):

    def __init__(self, x: int, y: int, image_path: str, vel: int, win_size: (int, int), callback):
        """
        :param x: x position
        :param y: y position
        :param image_path: path to image location
        :param vel: velocity
        :param win_size: size of window
        :param callback: callback method, when parachute fall off the screen, callback to para_fall
        """
        super().__init__(x, y, image_path, vel, win_size)
        # hit box: for collision detection, at the bottom of image
        self.hit_box = pygame.Rect(self.x, self.y + self.img.get_width() - 10, self.img.get_width(), 10)
        self.para_fall = callback

    def move(self):
        self.y += self.vel
        self.hit_box = pygame.Rect(self.x, self.y + self.img.get_width() - 10, self.img.get_width(), 10)

        # checks if parachute is out of window
        if self.y > self.win_height:
            self.para_fall(self)

    def draw(self, window: pygame.Surface):
        window.blit(self.img, (self.x, self.y))
        # pygame.draw.rect(window, (255, 0, 0), self.hit_box, 2)


class Airplane(ImageDrawable):

    def __init__(self, x: int, y: int, image_path: str, vel: int, win_size: (int, int), callback):
        """
        :param x: x position
        :param y: y position
        :param image_path: path to image location (Already as string)
        :param vel: velocity
        :param win_size: window size (width , height)
        :param callback: function, add_parachute to para_list
        """
        super().__init__(x, y, image_path, vel, win_size)
        # this image is too small and flipped, therefor:
        self.img = pygame.transform.flip(pygame.transform.scale2x(self.img), True, False)
        self.add_parachute = callback
        # choose random x for dropping the parachute
        self.drop_parachute_x = random.randint(0 + self.img.get_width(), self.win_width - self.img.get_width())
        self.isDropped = False  # ensures only one fall on each new track

    def move(self):
        self.x -= self.vel
        if self.x <= self.drop_parachute_x and not self.isDropped:
            self.add_parachute(self.x, self.y)  # add new para to list
            self.isDropped = True  # and only one!
        if self.x < -self.img.get_width():
            # airplane is out of screen, make it start again from the right
            self.x = self.win_width
            self.isDropped = False  # dont forget to drop new parachute
            # get new drop x
            self.drop_parachute_x = random.randint(0 + self.img.get_width(), self.win_width - self.img.get_width())

    def draw(self, window: pygame.Surface):
        window.blit(self.img, (self.x, self.y))


class Player(ImageDrawable):

    def __init__(self, x, y, image_path: str, vel: int, win_size: (int, int)):
        super().__init__(x, y, image_path, vel, win_size)
        # player should be at the bottom of the screen and centered
        self.x = (self.win_width - self.img.get_width()) // 2
        self.y = self.win_height - self.img.get_height()
        # hit box for collide detection
        self.hit_box = pygame.Rect(self.x, self.y + round(self.img.get_height() * 0.67), self.img.get_width(), 20)

    def move(self):
        """
        player can move base on pressed arrow keys (left, right)
        :return: None
        """
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and self.x > self.vel:
            self.x -= self.vel

        if keys[pygame.K_RIGHT] and self.x < self.win_width - self.vel - self.img.get_width():
            self.x += self.vel

        self.hit_box = pygame.Rect(self.x, self.y + round(self.img.get_height() * 0.67), self.img.get_width(), 20)

    def draw(self, window: pygame.Surface):
        window.blit(self.img, (self.x, self.y))


class Base(ImageDrawable):
    def __init__(self, x: int, y: int, image_path: str, vel: int, win_size: (int, int)):
        super().__init__(x, y, image_path, vel, win_size)
        # for animation, takes same image twice, and move them together.
        # when one image gets out of screen, get that image to starting position
        self.img1 = self.img
        self.img2 = pygame.transform.flip(self.img1, True, False)
        self.x1 = x
        self.x2 = self.img.get_width()

    def move(self):
        """
        move background (make sure to replace img position when img is out of frame)
        :return: None
        """
        self.x1 += self.vel
        self.x2 += self.vel
        if self.x1 > self.img.get_width():
            self.x1 = self.x2 - self.img.get_width()

        if self.x2 > self.img.get_width():
            self.x2 = self.x1 - self.img.get_width()

    def draw(self, window):
        window.blit(self.img1, (self.x1, self.y))
        window.blit(self.img2, (self.x2, self.y))


class GameLogic:
    """
    contains the logic of the game:
    status (update live & score)
    initialize all the components of game (player, parachutes, airplane..)
    keeps track of lives - for updating end of game
    and more
    """

    def __init__(self, window: pygame.Surface):
        self.win = window
        self.score = 0
        self.lives = cfg_logic["lives"]
        self.images = list()
        self.PAUSE: bool = False
        self.END_GAME: bool = False
        # parachutes list
        self.para_list: List[Parachute] = list()
        # player
        self.player = None

    def init(self) -> None:
        """
        init all images, and append to list - for iterate later when moving and drawing
        notice: the parachute list is NOT added, because its not ImageDrawable - it is a List
        of ImageDrawable
        :return: None
        """
        # init background: (can write it in one long line - but I prefer make it more readable
        x = cfg_bg["x"]
        y = cfg_bg["y"]
        path = os.path.join(*cfg_bg["path"])  # path is list..
        vel = cfg_bg["vel"]
        # add background to images for moving and drawing
        self.images.append(Base(x, y, path, vel, self.win.get_size()))

        # init airplane: (can write it in one long line - but I prefer make it more readable
        x = self.win.get_width()  # should start at the right side (x-axis) of window
        y = 0  # top of window (y-axis)
        path = os.path.join(*cfg_airplane["path"])
        vel = cfg_airplane["vel"]
        # add airplane to images for moving and drawing
        self.images.append(Airplane(x, y, path, vel, self.win.get_size(), callback=self.add_para))

        # init player: (can write it in one long line - but I prefer make it more readable
        # player will start at the middle of window, but its depends of img size!
        # so, I'll defined the position inside the constructor
        x = -1  # redefined inside the constructor
        y = -1  # redefined inside the constructor
        path = os.path.join(*cfg_player["path"])
        vel = cfg_player["vel"]
        # add airplane to images for moving and drawing
        self.player = Player(x, y, path, vel, self.win.get_size())
        self.images.append(self.player)

    def move_all(self) -> None:
        """
        moving all images.
        step 1: all images in images list
        step 2: all parachutes in parachute list
        :return: None
        """
        # moving all images except parachutes
        for img in self.images:
            img.move()
        # moving parachutes images
        for para in self.para_list:
            para.move()

    def draw_game(self) -> None:
        """
        drawing window, with all images
        step 1: all images in images list
        step 2: all parachutes in parachute list
        :return: None
        """
        # background:
        self.win.fill(pygame.Color(cfg_style["bg_color"]))
        # score
        font = pygame.font.SysFont(cfg_style["font"], cfg_style["font_bar_size"], bold=True)
        score = font.render('score: {}'.format(self.score), 1, pygame.Color(cfg_style["font_bar_color"]))
        # self.win.blit(score, (cfg_style["bar_x"], cfg_style["bar_y"]))
        self.win.blit(score, (0, 0))
        # lives:
        lives = font.render('lives: {}'.format(self.lives), 1, (0, 0, 0))
        self.win.blit(lives, (self.win.get_width() - lives.get_width(), 0))
        # images (without parachutes)
        for img in self.images:
            img.draw(self.win)
        # parachutes images
        for para in self.para_list:
            para.draw(self.win)

        pygame.display.update()

    def draw_pause(self):
        font = pygame.font.SysFont(cfg_style["font"], cfg_style["font_info_size"])
        text = font.render('Paused', 1, pygame.Color(cfg_style["font_info_color"]))

        # pose at mid of the window
        x = (self.win.get_width() - text.get_width()) // 2
        y = (self.win.get_height() - text.get_height()) // 2
        self.win.blit(text, (x, y))
        pygame.display.update()

    def draw_end(self):
        font = pygame.font.SysFont(cfg_style["font"], cfg_style["font_info_size"])
        text = font.render('Score {}'.format(self.score), 1, pygame.Color(cfg_style["font_info_color"]))

        # pose at mid of the window
        x = (self.win.get_width() - text.get_width()) // 2
        y = (self.win.get_height() - text.get_height()) // 2
        self.win.blit(text, (x, y))
        pygame.display.update()

    def game_status(self) -> None:
        """
        check the game status i.e: collisions, end o game.
        :return: None
        """
        # check end Game (3 strikes)
        if self.lives <= 0:
            self.END_GAME = True

        # check for collisions
        for para in self.para_list:
            if self.player.hit_box.colliderect(para.hit_box):
                self.para_collide(para)

    def score_update(self, x: int) -> None:
        """
        literally update score
        :param x: amount to add
        :return: None
        """
        self.score += x

    def pause_update(self):
        self.PAUSE = not self.PAUSE

    def add_para(self, x: int, y: int) -> None:
        """
        append new parachute to para_list at x,y
        :param x: x position
        :param y: y position
        :return: None
        """

        para = Parachute(x, y, os.path.join(*cfg_para["path"]), cfg_para["vel"], self.win.get_size(),
                         callback=self.para_fall)
        self.para_list.append(para)

    def para_fall(self, para: Parachute) -> None:
        """
        when para fall out of screen, remove from para_list, and subtract 1 from lives
        :param para: parachute to remove
        :return: None
        """
        self.lives -= 1
        self.para_list.remove(para)

    def para_collide(self, para: Parachute) -> None:
        """
        when parachute collide with player: remove the parachute and add 10 points
        :param para:
        :return: None
        """
        self.score_update(cfg_logic["score_update"])  # TODO: magic number - change!
        self.para_list.remove(para)


def game_loop(win, clock, fps):

    game = GameLogic(win)
    game.init()  # initialize all components for game

    while True:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not game.END_GAME:
                game.pause_update()

        if game.END_GAME:
            game.draw_end()
        elif game.PAUSE:
            game.draw_pause()
        else:
            game.move_all()
            game.draw_game()
            # check game logic status (update score, update life, remove finished parachutes, check collisions)
            game.game_status()


def draw_pre_game(win: pygame.Surface):
    font1 = pygame.font.SysFont(cfg_style["font"], 100)
    font2 = pygame.font.SysFont(cfg_style["font"], 75)
    font3 = pygame.font.SysFont(cfg_style["font"], 50)

    cur_y = 0
    win.fill((0, 0, 0))
    text1 = font1.render('Catch The Penguin', 1, pygame.Color(cfg_style["font_info_color"]))
    x = (win.get_width() - text1.get_width()) // 2
    win.blit(text1, (x, 0))
    cur_y += text1.get_height()

    text = font2.render('KEYS:', 1, pygame.Color(cfg_style["font_info_color"]))
    x = win.get_width() // 8
    win.blit(text, (x, cur_y + text.get_height()))
    cur_y += text.get_height() * 2

    text = font3.render('Press right/left Arrow to move', 1, pygame.Color(cfg_style["font_info_color"]))
    win.blit(text, (x, cur_y))
    cur_y += text.get_height()

    text = font3.render('Press SPACE to Pause', 1, pygame.Color(cfg_style["font_info_color"]))
    win.blit(text, (x, cur_y))
    cur_y += text.get_height()

    text = font3.render('Press ESC to Quit', 1, pygame.Color(cfg_style["font_info_color"]))
    win.blit(text, (x, cur_y))
    cur_y += text.get_height()

    text1 = font2.render('Press SPACE to continue', 1, pygame.Color(cfg_style["font_info_color"]))
    x = (win.get_width() - text1.get_width()) // 2
    win.blit(text1, (x, win.get_height() - text1.get_height()))

    pygame.display.update()


def pre_game_loop(win, clock, fps, callback):
    while True:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return callback(win, clock, fps)
        draw_pre_game(win)


def main() -> None:
    """
    Responsible for game loops
    :return: None
    """
    fps = cfg_win["clock"]  # frames per second (for making the game animated better)

    win = pygame.display.set_mode((cfg_win["width"], cfg_win["height"]))  # creates window
    pygame.display.set_caption(cfg_win["caption"])
    clock = pygame.time.Clock()

    # start pre game loop, and if needed start game loop (if player pressed Space)
    pre_game_loop(win, clock, fps, game_loop)

    pygame.quit()


if __name__ == '__main__':
    logging.basicConfig(filename='basic.log', level=logging.DEBUG, format='%(asctime)s: %(levelname)s: %(message)s')

    try:
        cfg = json.load(open('config.json'))
        cfg_win = cfg["window"]
        cfg_logic = cfg["gameLogic"]
        cfg_player = cfg["player"]
        cfg_bg = cfg["background"]
        cfg_airplane = cfg["airplane"]
        cfg_style = cfg["style"]
        cfg_para = cfg["parachute"]

    except OSError:
        logging.error('config file is missing')
        raise

    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.init()

    main()
