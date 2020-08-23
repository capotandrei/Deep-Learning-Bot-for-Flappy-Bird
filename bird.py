import pygame
from utils import BIRD_IMG, BG_IMG, WIN_WIDTH, WIN_HEIGHT


class Bird:
    IMGS = BIRD_IMG
    MAX_ROTATION = 25  # degrees
    ROT_VEL = 20  # rotation every frame
    ANIMATION_TIME = 5  # how fast the bird will move its wings

    # Starting positions for our bird
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0  # first time is flat
        self.tick_count = 0  # for phisic
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5  # velocity to jump
        self.tick_count = 0  # a counter to keep track when we last jumped
        self.height = self.y

    def move(self):
        self.tick_count += 1

        # d = v * t + a * t^2
        d = self.vel * self.tick_count + 1.5 * self.tick_count ** 2

        if d >= 16:  # way too far down (more than 16 pixels)
            d = 16
        if d < 0:  # if you go up, go a little bit more
            d -= 2

        self.y = self.y + d

        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt = self.ROT_VEL

    def draw(self, win):
        self.img_count += 1  # number of frames

        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:  # here we reset the image
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt < -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        # to rotate the image around the center
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)

        # Print the image on the screen
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)
