import enum


class FileType(enum.Enum):
    TYPE_MOV = 'mov'
    TYPE_HEIC = 'heic'
    TYPE_JPEG = 'jpg'
    TYPE_PNG = 'png'
    TYPE_MP4 = 'png'
    TYPE_CR3 = 'cr3'
    TYPE_DNG = 'dng'

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

    @staticmethod
    def detect_type(filename):
        fn = filename.lower()

        if fn.find('.mov') > 0:
            return FileType.TYPE_MOV
        elif fn.find('.heic') > 0:
            return FileType.TYPE_HEIC
        elif fn.find('.jpg') > 0 or fn.find('.jpeg') > 0:
            return FileType.TYPE_JPEG
        elif fn.find('.png') > 0:
            return FileType.TYPE_PNG
        elif fn.find('.mp4') > 0:
            return FileType.TYPE_MP4
        elif fn.find('.cr3') > 0:
            return FileType.TYPE_CR3
        elif fn.find('.dng') > 0:
            return FileType.TYPE_DNG

        raise ValueError('Filename has an unsupported format!')
