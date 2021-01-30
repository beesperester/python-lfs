import os

from pathlib import Path

from lfs.config import config_instance


class Repository:

    def __init__(
        self,
        name: str
    ) -> None:
        self._name = name

        if not os.path.isdir(self.GetPath()):
            os.makedirs(self.GetPath(), mode=0o777, exist_ok=True)

    def GetPath(self) -> str:
        return os.path.join(
            config_instance.GetRoot(),
            self.GetName()
        )

    def GetUrl(self) -> str:
        return "/".join([
            config_instance.GetUrl(),
            self.GetName()
        ])

    def GetName(self) -> str:
        return self._name

    def GetFileUrl(self, oid: str) -> str:
        return "/".join([
            self.GetUrl(),
            "info",
            "lfs",
            oid
        ])

    def GetFilePath(self, oid: str) -> Path:
        return Path(os.path.join(
            self.GetPath(),
            "info",
            "lfs",
            oid
        ))
