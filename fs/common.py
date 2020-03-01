import os
from typing import Optional

from model import File


class Directory:
    EXCLUDED_DIR_NAME = '_NotDated'

    def __init__(self, directory: str):
        self.__dir = directory
        self.__excluded = [Directory.EXCLUDED_DIR_NAME]

    def __do_fetch(self, directory: str):
        for file in sorted(os.listdir(directory)):
            if file in self.__excluded:
                continue

            file_path = os.path.join(directory, file)
            if os.path.isdir(file_path):
                results = [child_file for child_file in self.__do_fetch(file_path)]
            else:
                results = [file_path]

            # Return the files
            for fp in results:
                if isinstance(fp, File):
                    yield fp
                    continue

                yield File(fp)

    def fetch(self, file_extension: Optional[list] = None):
        for file in self.__do_fetch(self.__dir):
            if file_extension is None or file.extension.lower() in file_extension:
                yield file
