import pygame as pg

BACKGROUND_COLOR = 'white'
KNOWN_RESOLUTIONS = {
    '1080p': (1920, 1080),
    '720p': (1280, 720),
    '480p': (640, 480),
    '800x600': (800, 600),
    '640x480': (640, 480)
}
WINDOW_RESOLUTION = KNOWN_RESOLUTIONS['720p']
