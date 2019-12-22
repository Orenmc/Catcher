import pygame
import os
import json
import logging


class Obj:

    def __init__(self, config: dict):
        self.x = config["x"]
        self.y = config["y"]
        self.img = [self.x, self.y, config["width"], config["height"]]
        self.vel = config["vel"]
        # self.rect = [cfg["x"], cfg["height"] - cfg["height"], cfg["width"], cfg["height"]]

    def move(self, keys):

        if keys[pygame.K_LEFT] and self.img[0] > self.vel:
            self.img[0] -= self.vel
        if keys[pygame.K_RIGHT] and self[0] < (win_cfg["width"] - obj_cfg["width"] - self.vel):
            rect[0] += self.vel
        if keys[pygame.K_UP] and rect[1] > vel:
            rect[1] -= self.vel
        if keys[pygame.K_DOWN] and rect[1] < win_cfg["height"] - obj_cfg["height"] - self.vel:
            rect[1] += self.vel

    def draw(self, win: pygame.Surface):
        win.fill((0, 0, 0))
        pygame.draw.rect(win, (255, 0, 0), self.img)
        pygame.display.update()


def main(config: dict) -> None:
    win_cfg = config["win"]
    win = pygame.display.set_mode((win_cfg["width"], win_cfg["height"]))

    pygame.display.set_caption(win_cfg["caption"])
    clock = pygame.time.Clock()

    rect = Obj(config["object"])

    run = True
    while run:
        clock.tick(win_cfg["clock"])
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # keys = pygame.key.get_pressed()

        # win.fill((0, 0, 0))
        # pygame.draw.rect(win, (255, 0, 0), rect)
        # pygame.display.update()
        rect.draw(win)

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
    main(cfg)
