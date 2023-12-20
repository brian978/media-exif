import abc
import struct
import subprocess
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Optional

import exifread
import xml.etree.ElementTree as ET

from fs.ftype import FileType
from model import File


class AbstractMeta(abc.ABC):
    def __init__(self, filename: str):
        self._filename = filename

    def get_create_timestamp(self) -> Optional[datetime]:
        pass


class MetaFactory:
    @staticmethod
    def factory(file: File) -> AbstractMeta:
        if file.type == FileType.TYPE_MOV:
            return MovMeta(file.name)
        elif file.type == FileType.TYPE_JPEG:
            return JpgMeta(file.name)
        elif file.type == FileType.TYPE_PNG:
            return PngMeta(file.name)
        elif file.type == FileType.TYPE_HEIC:
            return HeicMeta(file.name)
        elif file.type == FileType.TYPE_CR3:
            return Cr3Meta(file.name)
        elif file.type == FileType.TYPE_DNG:
            return DngMeta(file.name)


class MovMeta(AbstractMeta):
    @staticmethod
    def __has_moov_header(fh):
        try:
            while True:
                header = fh.read(8)
                if header[4:8] == b'moov':
                    return True
                else:
                    atom_size = struct.unpack('>I', header[0:4])[0]
                    fh.seek(atom_size - 8, 1)
        except BaseException as be:
            print('Error: ' + be.__str__())
        except EOFError as eof:
            print('Reached the end of file but did not find the MOOV header')

        return False

    def get_create_timestamp(self) -> Optional[datetime]:
        atom_header_size = 8
        epoch_adjuster = 2082844800  # difference between Unix epoch and QuickTime epoch, in seconds

        creation_time = None
        # modification_time = None

        # search for moov item
        with open(self._filename, "rb") as f:
            if not self.__has_moov_header(f):
                print('Did not find any MOOV header')
                return None

            # found 'moov', look for 'mvhd' and timestamps
            atom_header = f.read(atom_header_size)
            if atom_header[4:8] == b'cmov':
                print('moov atom is compressed')
                return None
            elif atom_header[4:8] != b'mvhd':
                print('expected to find "mvhd" header.')
                return None
            else:
                f.seek(4, 1)

                creation_time = struct.unpack('>I', f.read(4))[0] - epoch_adjuster
                creation_time = datetime.fromtimestamp(creation_time)
                if creation_time.year < 1990:  # invalid or censored data
                    creation_time = None

                # modification_time = struct.unpack('>I', f.read(4))[0] - epoch_adjuster
                # modification_time = datetime.fromtimestamp(modification_time)
                # if modification_time.year < 1990:  # invalid or censored data
                #     modification_time = None

        return creation_time


class HeicMeta(AbstractMeta):
    def get_create_timestamp(self) -> Optional[datetime]:
        local_tz = timezone(timedelta(hours=3))

        """Gets the date taken for a photo through a shell."""
        cmd = "mdls '%s'" % self._filename
        output = subprocess.check_output(cmd, shell=True)

        lines = output.decode("ascii").split("\n")
        for line in lines:
            if "kMDItemContentCreationDate" in line:
                datetime_str = line.split("= ")[1]
                dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S %z") + timedelta(hours=3)
                dt.replace(tzinfo=local_tz)

                return dt

        return None


class Mp4Meta(AbstractMeta):
    def get_create_timestamp(self) -> Optional[datetime]:
        atom_header_size = 8
        epoch_adjuster = 2082844800  # difference between Unix epoch and QuickTime epoch, in seconds

        # search for moov item
        with open(self._filename, "rb") as f:
            # found 'moov', look for 'mvhd' and timestamps
            atom_header = f.read(atom_header_size)
            if atom_header[4:8] == b'cmov':
                print('moov atom is compressed')
                return None
            elif atom_header[4:8] != b'mvhd':
                print('expected to find "mvhd" header.')
                return None

            f.seek(4, 1)

            creation_time = struct.unpack('>I', f.read(4))[0] - epoch_adjuster
            creation_time = datetime.fromtimestamp(creation_time)
            if creation_time.year < 1990:  # invalid or censored data
                creation_time = None

        return creation_time


class JpgMeta(AbstractMeta):
    def get_create_timestamp(self) -> Optional[datetime]:
        f = open(self._filename, 'rb')

        # Return Exif tags
        tags = exifread.process_file(f)
        exif_date = None

        if 'Image DateTime' in tags:
            exif_date = str(tags['Image DateTime'])
        elif 'EXIF DateTimeOriginal' in tags:
            exif_date = str(tags['EXIF DateTimeOriginal'])

        if exif_date is not None and len(exif_date):
            return datetime.strptime(exif_date, '%Y:%m:%d %H:%M:%S')

        return None


class PngMeta(AbstractMeta):
    def get_create_timestamp(self) -> Optional[datetime]:
        create_timestamp = None

        with open(self._filename, 'rb') as fh:
            fh.seek(2)
            while True:
                chunk = fh.read(4)

                if chunk == b'eXIf':
                    fh.seek(658, 1)
                    timestamp = fh.read(26).decode('utf8').replace('\x00', ' ')
                    create_timestamp = datetime.strptime(timestamp, "%Y:%m:%d %H:%M:%S %z")
                    break
                elif chunk == b'':
                    break

        if create_timestamp is None:
            create_timestamp = self.get_create_timestamp_from_xml()

        return create_timestamp

    def get_create_timestamp_from_xml(self):
        create_timestamp = None

        with open(self._filename, 'rb') as fh:
            data = fh.read()
            is_xmp = data.find(b'com.adobe.xmp') != 0

            if is_xmp:
                start_tag_offset = data.find(b'<x:xmpmeta')
                end_tag_offset = data.find(b'</x:xmpmeta>') + len(b'</x:xmpmeta>')
                xml_string = data[start_tag_offset:end_tag_offset].decode('utf8')

                root = ET.fromstring(xml_string)
                created_date_tag = root.find('.//{http://ns.adobe.com/xap/1.0/}CreateDate')

                if created_date_tag is not None:
                    create_timestamp = datetime.strptime(created_date_tag.text, "%Y-%m-%dT%H:%M:%S")

        return create_timestamp


class Cr3Meta(AbstractMeta):
    def get_create_timestamp(self) -> Optional[datetime]:
        create_timestamp = None

        with open(self._filename, 'rb') as fh:
            # Seek to byte
            fh.seek(524, 0)

            try:
                timestamp = fh.read(20).decode('utf8').replace('\x00', '')
                create_timestamp = datetime.strptime(timestamp, "%Y:%m:%d %H:%M:%S")
                # print(f'Found timestamp: {create_timestamp}')
            except ValueError as e:
                print(f'Invalid position for timestamp in file {self._filename}')
                print(f'Error message: {str(e)}')

        return create_timestamp


class DngMeta(AbstractMeta):
    def get_create_timestamp(self) -> Optional[datetime]:
        create_timestamp = None

        with open(self._filename, 'rb') as fh:
            # Seek to byte
            fh.seek(448, 0)

            try:
                timestamp = fh.read(20).decode('utf8').replace('\x00', '')
                create_timestamp = datetime.strptime(timestamp, "%Y:%m:%d %H:%M:%S")
            except ValueError as e:
                print(f'Invalid position for timestamp in file {self._filename}')
                print(f'Error message: {str(e)}')

        return create_timestamp
