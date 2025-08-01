import abc
import pathlib

import pdfminer.high_level
import PyPDF2


__all__ = []


class TextExtractor(abc.ABC):
    def __init__(self, file: pathlib.Path | None = None):
        self.file = None
        if file is not None:
            self.upload_file(file)

    @abc.abstractmethod
    def get_text(self) -> str:
        pass

    @abc.abstractmethod
    def upload_file(self, file: pathlib.Path):
        pass


class PyPDF2Extractor(TextExtractor):
    def get_text(self):
        pdf_book = PyPDF2.PdfReader(self.file)
        return ''.join(page.extract_text() for page in pdf_book.pages)

    def upload_file(self, file: pathlib.Path):
        if not file:
            raise ValueError

        self.file = file


class PDFMinerExtractor(TextExtractor):
    def get_text(self):
        return pdfminer.high_level.extract_text(self.file)

    def upload_file(self, file: pathlib.Path):
        if not file:
            raise ValueError

        self.file = file
