import os
import shutil

from fs.common import Directory
from fs.ftype import FileType
from media.metadata import MetaFactory

path = input('Target path: ')
# path = os.path.abspath('./resources')

print(f'Lookup directory: {path}')

dir_obj = Directory(path)

for file in dir_obj.fetch(FileType.list()):
    print(f'-------- Processing file {file.name}')
    print(f'#')

    try:
        file_meta = MetaFactory.factory(file)

        date = file_meta.get_create_timestamp()
        if date is not None:
            print(f'Tagging file {file.basename} with date {date}')

            file.create_timestamp = date
            file.save()
        else:
            print(f'No date taken for file: {file.basename}')

            file_dir = os.path.dirname(file.name)
            not_dated = os.path.join(file_dir, Directory.EXCLUDED_DIR_NAME)

            if not os.path.isdir(not_dated):
                os.mkdir(not_dated)

            # making sure the file does not exist
            new_filename = f'{not_dated}/{file.basename}'
            while os.path.isfile(new_filename):
                new_filename = f'{not_dated}/{file.create_unique_basename()}'

            print(f'Copy from {file.name} to {new_filename}')
            shutil.move(file.name, new_filename)
    except ValueError as msg:
        print(f'{file.name}: {msg}')
        continue
    finally:
        print(f'#')
        print(f'-------------- End processing for file {file.basename}----------------------')
        print('')
