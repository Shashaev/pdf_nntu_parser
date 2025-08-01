import pathlib
import typing


__all__ = []


class JSONSaver:
    @typing.overload
    def __init__(self, root_path: pathlib.Path):
        self.root_path = root_path

    @typing.overload
    def __init__(self, root_path: str):
        self.root_path = pathlib.Path(root_path)

    def save_json(
        self,
        name: str,
        file: str,
        category: str = '',
        overwriting: bool = True,
    ):
        if name[-5:] != '.json':
            name = f'{name}.json'

        path_file: pathlib.Path = self.root_path + category + name
        if path_file.exists() and not overwriting:
            raise FileExistsError

        path_file.write_text(file)
