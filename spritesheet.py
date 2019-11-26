import pygame
from functools import lru_cache
from util import COLOR_BLACK_KEY


class SpriteSheet:
    def __init__(self, filename, sprite_size=8, upsample=1):
        self.sprite_size = sprite_size
        self.upsample = upsample
        self.sheet = pygame.image.load(filename).convert()

    @staticmethod
    def crop(source_image: pygame.Surface, rect):
        _, _, w, h = rect
        old_colorkey = source_image.get_colorkey()
        image = pygame.Surface((w, h)).convert()
        image.blit(source_image, (0, 0), rect)
        image.set_colorkey(old_colorkey)
        return image

    @lru_cache(maxsize=None)
    def image_at(self, x, y, w=1, h=1, colorkey=COLOR_BLACK_KEY, auto_crop=False,
                 square=False):
        s = self.sprite_size
        rect = pygame.Rect(x * s, y * s, w * s, h * s)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)

        new_size = s * self.upsample

        if self.upsample != 1:
            image = pygame.transform.scale(image, (w * new_size, h * new_size))

        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)

        if auto_crop:
            image = self.crop(image, self.find_crop_rect(image, square=square))

        return image

    @staticmethod
    def find_crop_rect(img, bg_color=COLOR_BLACK_KEY, square=False):
        w, h = img.get_width(), img.get_height()

        def scan_line(or_x, or_y, horizontal):
            line_x = range(w) if horizontal else [or_x] * w
            line_y = [or_y] * h if horizontal else range(h)
            line_xy = zip(line_x, line_y)
            return all(img.get_at((x, y)) == bg_color for x, y in line_xy)

        left, right, top, bottom = 0, 0, 0, 0

        while left < w:
            if not scan_line(left, 0, horizontal=False):
                break
            left += 1

        while right < w:
            if not scan_line(w - 1 - right, 0, horizontal=False):
                break
            right += 1

        while top < h:
            if not scan_line(0, top, horizontal=True):
                break
            top += 1

        while bottom < h:
            if not scan_line(0, h - bottom - 1, horizontal=True):
                break
            bottom += 1


        crop_w = w - right - left
        crop_h = h - bottom - top

        if square:
            d = crop_w - crop_h
            if d > 0:
                top -= d // 2
                crop_h = crop_w
            else:
                left -= d // 2
                crop_w = crop_h

        return left, top, crop_w, crop_h
    @property
    def real_sprite_size(self):
        return self.sprite_size * self.upsample
