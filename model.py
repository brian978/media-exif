import os
from datetime import datetime
from typing import Optional

from fs.ftype import FileType


class File:
    def __init__(self, filename: str):
        """
        File object constructor

        :param str filename: Full path of the file
        """
        self.__filename = filename
        self.__properties = {}
        self.__dupe_idx = 0

    @property
    def name(self):
        return self.__filename

    @property
    def basename(self):
        return os.path.basename(self.__filename)

    @property
    def extension(self):
        basename = self.basename
        pcs = basename.split('.')
        return ''.join(pcs[-1:])

    @property
    def type(self):
        return FileType.detect_type(self.__filename)

    @property
    def create_timestamp(self) -> Optional[datetime]:
        """
        Getter for the file creation timestamp

        :return: Returns a datetime object
        :rtype: datetime
        """
        if 'create_timestamp' not in self.__properties:
            self.__properties['create_timestamp'] = None

        return self.__properties['create_timestamp']

    @create_timestamp.setter
    def create_timestamp(self, value: datetime):
        """
        Setter for the file creation timestamp

        :param value:
        :return:
        """
        self.__properties['create_timestamp'] = value

    def create_unique_basename(self) -> str:
        """
        Creates a unique filename to avoid file overwrite

        :return: Returns a unique name f    or the basename
        :rtype: str
        """
        self.__dupe_idx += 1

        parts = self.basename.split('.')
        extension = ''.join(parts[-1:])
        name = '.'.join(parts[:-1])

        return f'{name} ({self.__dupe_idx}).{extension}'

    def save(self) -> None:
        """
        Save the file info

        :return: Nothing
        :rtype: None
        """
        if self.create_timestamp is not None:
            os.utime(self.__filename, (self.create_timestamp.timestamp(), self.create_timestamp.timestamp()))
