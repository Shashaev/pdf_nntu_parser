import colorama
import logging
import typing
import sys

import settings


__all__ = []


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        if record.levelno >= logging.ERROR:
            color = colorama.Fore.RED
        elif record.levelno >= logging.WARNING:
            color = colorama.Fore.YELLOW
        elif record.levelno >= logging.INFO:
            color = colorama.Fore.GREEN
        else:
            color = colorama.Fore.WHITE

        message = super().format(record)
        return f'{color}{message}{colorama.Fore.RESET}'


logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(
    ColoredFormatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    ),
)

logger.addHandler(handler)

colorama.init()
logging.basicConfig(
    filename=settings.PATH_DATA / 'app.log',
    level=logging.DEBUG,
)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').propagate = False
logging.info('The app has started working...')


def log_start_end(fun: typing.Callable):
    def inner(*args, **kwargs):
        logging.info(f' Start function - "{fun.__name__}" '.center(75, '='))
        ans = fun(*args, **kwargs)
        logging.info(f' End function "{fun.__name__}" '.center(75, '='))
        return ans

    return inner
