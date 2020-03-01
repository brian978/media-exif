import os
from typing import Optional

from model import File


class Directory:
    excluded = ['NotDated']

    def __init__(self, directory: str):
        self.__dir = directory

    def __do_fetch(self, directory: str):
        for file in sorted(os.listdir(directory)):
            if file in Directory.excluded:
                continue

            file_path = os.path.join(directory, file)
            if os.path.isdir(file_path):
                results = [child_file for child_file in self.__do_fetch(file_path)]
            else:
                results = [file_path]

            # Return the files
            for fp in results:
                yield File(fp)

    def fetch(self, file_extension: Optional[list] = None):
        for file in self.__do_fetch(self.__dir):
            if file_extension is None or file.extension in file_extension:
                yield file
