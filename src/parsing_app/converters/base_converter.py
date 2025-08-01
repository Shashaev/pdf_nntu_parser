import abc
import functools
import pathlib

import database.models as models


__all__ = []


class BlockParser(abc.ABC):
    def __init__(self, pdf: models.Base):
        self.pdf = pdf

    @abc.abstractmethod
    def parsing(self) -> pathlib.Path:
        pass

    @functools.lru_cache
    @abc.abstractmethod
    def is_exists_block(self) -> bool:
        pass

    @abc.abstractmethod
    def __str__():
        pass
