import logging

from colorlog import ColoredFormatter

color_formatter = ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s%(name)-10s %(blue)s%(message)s",
        datefmt=None,
        reset=True,
        log_colors={
                'DEBUG':    'cyan',
                'INFO':     'green',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
)


def init_logging():
    base_logger = logging.getLogger()
    base_logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    sh.setFormatter(color_formatter)
    base_logger.addHandler(sh)

going_right = 1  # 1=going right, 0=going left


def draw_kit(step, size):
    size = size - 1
    global going_right
    if going_right:
        left = '-' * (step + 1)
        right = '-' * (size - step)
    else:
        left = '-' * (size - step)
        right = '-' * (step + 1)
    cursor = '\x1b[31m#\x1b[0m'
    #print(cursor)
    print('\r %s%s%s\r' % (left, cursor, right), end='', flush=True)

    if step >= size:
        if going_right:
            going_right = 0
        else:
            going_right = 1
