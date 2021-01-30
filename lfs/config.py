import os


class Config:

    def __init__(self) -> None:
        self._root = ""
        self._url = ""

    def GetRoot(self) -> str:
        if not self._root:
            raise Exception("Root must be set")

        return self._root

    def SetRoot(self, path: str):
        assert os.path.isdir(path)

        self._root = path

    def SetUrl(self, url: str):
        self._url = url

    def GetUrl(self) -> str:
        if not self._url:
            raise Exception("Url must be set")

        return self._url


config_instance = Config()
