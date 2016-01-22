from uuid import uuid4
import logging
import signal

from colorlog import ColoredFormatter

logger = logging.getLogger('guenther')

color_formatter = ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s%(name)-14s %(blue)s%(message)s",
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


def draw_kit(step, size, fingerprint_count):
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
    print('\r %s%s%s fp: %s\r' % (left, cursor, right, fingerprint_count), end='', flush=True)

    if step >= size:
        if going_right:
            going_right = 0
        else:
            going_right = 1


def is_match_correct():
    def interrupted(signum, frame):
        print('')
        logger.info('No response from user, so NO.')
        raise TimeoutError('no response from user')
    signal.signal(signal.SIGALRM, interrupted)

    correct = False
    print('If you say this was correct, i will add it to the test data.')
    try:
        signal.alarm(5)
        input('Did you really say my name? (enter to confirm, wait to deny)')
        correct = True
    except TimeoutError:
        pass
    signal.alarm(0)
    return correct


def get_unique_name():
    return '%s.wav' % uuid4()
