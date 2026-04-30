from typing import IO, TextIO
from pathlib import Path
import soundfile as sf
import numpy as np
import os

from src.module.service.file_storage.disk_storage.service import DiskFileStorageService, Encoding


class DiskFileStorageServiceImpl(DiskFileStorageService):

    def __init__(self, dirpath: str, buffer_size: int):
        super().__init__(dirpath, buffer_size)

    def get_file(self, filename: str) -> IO:
        filepath = self.dirpath / Path(filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File by name '{filename} not found in '{self.dirpath}'.")

        with open(filename) as file:
            return file

    def create_text_file(self, filename: str, content_stream: TextIO, encoding: Encoding = Encoding.UTF_8) -> Path:
        filepath = self.get_unique_filepath(filename)
        content_stream.seek(0)

        with open(filepath, 'w', buffering=self.buffer_size, encoding=encoding.value) as file:
            seek = self.buffer_size
            while chunk := content_stream.read(seek):
                file.write(chunk)
                seek += self.buffer_size

        return filepath

    def create_sound_file(self, filename: str, audio_array: np.ndarray, sample_rate: int) -> Path:
        filepath = self.get_unique_filepath(filename)
        sf.write(filepath, audio_array, sample_rate)

        return filepath

    def get_unique_filepath(self, filename_template: str) -> Path:
        filepath = self.dirpath / Path(filename_template)
        if not os.path.exists(filepath):
            return filepath

        counter = 1
        while True:
            new_filepath = filepath.parent / f"{filepath.stem} ({counter}){filepath.suffix}"
            if not new_filepath.exists():
                return new_filepath
            counter += 1

    def set_new_file_extension(self, filename: str, extension: str) -> str:
        filename_elems = filename.rsplit('.')
        filename_elems[-1] = extension
        return '.'.join(filename_elems)
