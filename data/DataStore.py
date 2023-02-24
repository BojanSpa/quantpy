import pandas as pd
from zipfile import ZipFile


class DataStore:
    def save(self, file_path, directory):
        if (file_path.endswith('.zip')):
            self.__extract(file_path, directory)
    

    def __extract(self, file_path, directory):
        with ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(directory)