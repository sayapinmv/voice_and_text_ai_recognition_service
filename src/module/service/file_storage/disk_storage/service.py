from abc import ABC, abstractmethod
from typing import IO, TextIO
from pathlib import Path
from enum import Enum
import numpy as np

class AudioFileExtension(Enum):
    WAV = 'wav'
    MP3 = 'mp3'
    MP4 = 'mp4'
    MOV = 'MOV'
    OGG = 'ogg'


class TextFileExtension(Enum):
    TXT = 'txt'
    SRT = 'srt'


class Encoding(Enum):
    UTF_8 = 'utf-8'
    ASCII = 'ascii'
    UTF_16 = 'utf-16'
    UTF_32 = 'utf-32'

    def __str__(self):
        return self.value


class DiskFileStorageService(ABC):
    def __init__(self, dirpath: str, buffer_size: int):
        self.dirpath = dirpath
        self.buffer_size = buffer_size

    @abstractmethod
    def get_file(self, filename: str) -> IO: pass

    @abstractmethod
    def create_text_file(self, filename: str, content_stream: TextIO, encoding: Encoding = Encoding.UTF_8) -> Path: pass

    @abstractmethod
    def create_sound_file(self, filename: str, audio_array: np.ndarray, sample_rate: int) -> Path: pass

    @abstractmethod
    def get_unique_filepath(self, filename_template: str) -> Path: pass

    @abstractmethod
    def set_new_file_extension(self, filename: str, extension: str) -> str: pass
