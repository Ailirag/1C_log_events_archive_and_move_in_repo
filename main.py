import glob
import time
import zipfile
import shutil
import pathlib
import os
from datetime import datetime
import json


def logging(text):
    with open(f'{os.getcwd() + os.sep}log.txt', 'a', encoding='utf8') as log_file:
        for log_text in text.split('\n'):
            text_to_write = f'{datetime.now()} :   {log_text}'
            log_file.write(text_to_write + '\n')
            print(text_to_write)


class Settings(object):
    def __init__(self, file_name = None):
        if file_name is None:
            file_name = f'{os.getcwd() + os.sep}settings.json'
        self._path_to_settings = file_name

        with open(file_name, 'r', encoding='utf8') as settings_file:
            data = json.loads(settings_file.read())

        for key, value in data.items():
            self.__dict__[key] = value


def archiving_v8logs(settings, file_name):
    try:
        logging(f'          archiving date {file_name[:-4]}')
        name_archive = f'{settings["path_to_v8logs"]}{os.sep}{settings["archive_prefix"]}{file_name[:-4]}.zip'
        name_backup = f'{settings["backup_path"]}{os.sep}{settings["archive_prefix"]}{file_name[:-4]}.zip'
        with zipfile.ZipFile(name_archive, 'w') as myzip:
            myzip.write(f'{settings["path_to_v8logs"]}{os.sep}{file_name[:-4]}.lgx', arcname=f'{file_name[:-4]}.lgx',
                        compress_type=zipfile.ZIP_DEFLATED,
                        compresslevel=7)
            myzip.write(f'{settings["path_to_v8logs"]}{os.sep}{file_name}', arcname=file_name,
                        compress_type=zipfile.ZIP_DEFLATED, compresslevel=7)
            myzip.write(f'{settings["path_to_v8logs"]}{os.sep}1Cv8.lgf', arcname='1Cv8.lgf',
                        compress_type=zipfile.ZIP_DEFLATED, compresslevel=7)

        logging(f'          Deleting {file_name} and {file_name[:-3]}lgx')

        try:
            if os.path.exists(f'{settings["path_to_v8logs"]}{os.sep}{file_name}'):
                os.remove(f'{settings["path_to_v8logs"]}{os.sep}{file_name}')
            if os.path.exists(f'{settings["path_to_v8logs"]}{os.sep}{file_name[:-3]}lgx'):
                os.remove(f'{settings["path_to_v8logs"]}{os.sep}{file_name[:-3]}lgx')
        except Exception as e:
            logging('          Failed delete to delete log file. ' + str(type(e)) + str(e))

        logging(f'          Try to move in repo: {settings["backup_path"]}')
        shutil.move(name_archive, name_backup)

        logging(f'          Success')
    except Exception as e:
        error_exc = str(type(e)) + str(e)
        logging(f'              Action failed with an error: {error_exc}')


if __name__ == '__main__':

    data = Settings()

    logging('Start programm.')

    for folder in data.logs:

        logging(f'  Working with {folder["archive_prefix"]} - {folder["path_to_v8logs"]}')

        list_of_files = glob.glob(folder['path_to_v8logs'] + os.sep + '*.lgp')

        border = time.time() - (int(folder['count_of_days_without_archive'])) * 86400

        mas_to_move = list()

        for file in list_of_files:
            time_file = os.path.getmtime(file)
            if time_file <= border:
                mas_to_move.append(pathlib.Path(file).name)

        logging(f'      Count of file to move in repo: {len(mas_to_move)}')

        for file in mas_to_move:
            archiving_v8logs(folder, file)

        logging(f'      Complete - {folder["archive_prefix"]}')

    logging('Finish.')