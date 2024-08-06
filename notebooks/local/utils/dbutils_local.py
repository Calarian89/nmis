from dataclasses import dataclass
import os
import shutil


class DBUtilsLocal:
    """
    Class used to provide a minimal local version ofthe Databricks dbutils object
    that is auto-injected into their clusters/kernels.  Our notebooks mostly use the
    `fs` and `secrets` packages from it, so just provide some sensible local behavior
    alternatives for when those package functions are called.
    """

    def __init__(self):
        self.fs = DBUtilsLocal.Fs()
        self.secrets = DBUtilsLocal.Secrets()

    @dataclass
    class Fs:
        """
        dbutils `fs` package usually used for interacting with the dbfs file system.
        Leverage the os package heavily here to provide similar functionality for
        things like moving files, deleting them, or listing FileInfo objects.
        """

        @dataclass
        class FileInfo:
            name: str
            path: str
            size: int

        @staticmethod
        def ls(path: str) -> list[FileInfo]:
            return [
                DBUtilsLocal.Fs.FileInfo(
                    name, f"{path}/{name}", os.stat(f"{path}/{name}").st_size
                )
                for name in os.listdir(path)
            ]

        @staticmethod
        def head(path: str, max_bytes: int) -> str:
            with open(path, "r") as file:
                return file.read()[:max_bytes]

        @staticmethod
        def mv(from_path: str, to_path: str):
            os.renames(from_path, to_path)

        @staticmethod
        def put(path: str, content: str):
            dir = os.path.dirname(path)
            if not os.path.exists(dir):
                os.makedirs(dir)
            with open(path, "w") as file:
                file.write(content)

        @staticmethod
        def rm(path: str, force: bool = False):
            if os.path.isdir(path):
                if force:
                    shutil.rmtree(path)
                else:
                    os.rmdir(path)
            else:
                os.remove(path)

    @dataclass
    class Secrets:
        """
        dbutils `secrets` package used for interacting with secrets that have
        been uploaded to Databricks. Simply uses a dictionary to provide fake
        secret values back when running locally.
        """

        secret_store = {
            "NMIS": {
                "nmis_api_id": "nmis_api_id_value",
                "nmis_api_pwd": "nmis_api_pwd_value",
            }
        }

        def get(self, scope: str, key: str) -> str:
            return self.secret_store[scope][key]


# Make a singleton instance that can be used in our local notebooks and tests.
dbutils = DBUtilsLocal()
