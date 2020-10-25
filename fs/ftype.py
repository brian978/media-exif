import enum


class FileType(enum.Enum):
    TYPE_MOV = 'mov'
    TYPE_HEIC = 'heic'
    TYPE_JPEG = 'jpg'
    TYPE_PNG = 'png'
    TYPE_MP4 = 'png'

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

        raise ValueError('Filename has an unsupported format!')
